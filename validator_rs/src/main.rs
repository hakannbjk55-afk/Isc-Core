use serde::Deserialize;
use serde::de::{self, MapAccess, SeqAccess, Visitor};
use serde_json::{Number, Value};
use std::collections::{BTreeMap, HashSet};
use std::fmt;
use std::fs;

struct StrictValue(Value);

impl<'de> serde::Deserialize<'de> for StrictValue {
    fn deserialize<D>(deserializer: D) -> Result<Self, D::Error>
    where
        D: serde::Deserializer<'de>,
    {
        struct V;

        impl<'de> Visitor<'de> for V {
            type Value = StrictValue;

            fn expecting(&self, f: &mut fmt::Formatter) -> fmt::Result {
                write!(f, "a JSON value")
            }

            fn visit_bool<E>(self, v: bool) -> Result<Self::Value, E> {
                Ok(StrictValue(Value::Bool(v)))
            }

            fn visit_i64<E>(self, v: i64) -> Result<Self::Value, E> {
                Ok(StrictValue(Value::Number(Number::from(v))))
            }

            fn visit_u64<E>(self, v: u64) -> Result<Self::Value, E> {
                Ok(StrictValue(Value::Number(Number::from(v))))
            }

            fn visit_f64<E>(self, v: f64) -> Result<Self::Value, E>
            where
                E: de::Error,
            {
                let n = Number::from_f64(v).ok_or_else(|| de::Error::custom("invalid number"))?;
                Ok(StrictValue(Value::Number(n)))
            }

            fn visit_str<E>(self, v: &str) -> Result<Self::Value, E> {
                Ok(StrictValue(Value::String(v.to_owned())))
            }

            fn visit_string<E>(self, v: String) -> Result<Self::Value, E> {
                Ok(StrictValue(Value::String(v)))
            }

            fn visit_none<E>(self) -> Result<Self::Value, E> {
                Ok(StrictValue(Value::Null))
            }

            fn visit_unit<E>(self) -> Result<Self::Value, E> {
                Ok(StrictValue(Value::Null))
            }

            fn visit_seq<A>(self, mut seq: A) -> Result<Self::Value, A::Error>
            where
                A: SeqAccess<'de>,
            {
                let mut out = Vec::new();
                while let Some(x) = seq.next_element::<StrictValue>()? {
                    out.push(x.0);
                }
                Ok(StrictValue(Value::Array(out)))
            }

            fn visit_map<A>(self, mut map: A) -> Result<Self::Value, A::Error>
            where
                A: MapAccess<'de>,
            {
                let mut seen: HashSet<String> = HashSet::new();
                let mut entries: Vec<(String, Value)> = Vec::new();

                while let Some((k, v)) = map.next_entry::<String, StrictValue>()? {
                    if !seen.insert(k.clone()) {
                        return Err(de::Error::custom(format!("duplicate key: {}", k)));
                    }
                    entries.push((k, v.0));
                }

                let mut obj = serde_json::Map::new();
                for (k, v) in entries {
                    obj.insert(k, v);
                }
                Ok(StrictValue(Value::Object(obj)))
            }
        }

        deserializer.deserialize_any(V)
    }
}

fn parse_strict(s: &str) -> Result<Value, String> {
    let mut de = serde_json::Deserializer::from_str(s);
    let StrictValue(v) = <StrictValue as Deserialize>::deserialize(&mut de).map_err(|e| e.to_string())?;
    de.end().map_err(|e| e.to_string())?;
    Ok(v)
}

fn normalize_negative_zero(v: &mut Value) {
    match v {
        Value::Number(n) => {
            let s = n.to_string();
            if s.starts_with("-0") {
                if let Some(f) = n.as_f64() {
                    if f == 0.0 {
                        *n = Number::from(0);
                    }
                }
            }
        }
        Value::Array(a) => {
            for x in a.iter_mut() {
                normalize_negative_zero(x);
            }
        }
        Value::Object(o) => {
            for (_k, x) in o.iter_mut() {
                normalize_negative_zero(x);
            }
        }
        _ => {}
    }
}

fn write_number(out: &mut String, n: &Number) {
    if let Some(i) = n.as_i64() {
        out.push_str(&i.to_string());
    } else if let Some(u) = n.as_u64() {
        out.push_str(&u.to_string());
    } else if let Some(f) = n.as_f64() {
        if f.fract() == 0.0 {
            out.push_str(&(f as i64).to_string());
        } else {
            out.push_str(&n.to_string());
        }
    } else {
        out.push_str(&n.to_string());
    }
}

fn canon_value(out: &mut String, v: &Value) {
    match v {
        Value::Null => out.push_str("null"),
        Value::Bool(b) => out.push_str(if *b { "true" } else { "false" }),
        Value::Number(n) => write_number(out, n),
        Value::String(s) => out.push_str(&serde_json::to_string(s).unwrap()),
        Value::Array(a) => {
            out.push('[');
            let mut first = true;
            for x in a {
                if !first {
                    out.push(',');
                }
                first = false;
                canon_value(out, x);
            }
            out.push(']');
        }
        Value::Object(o) => {
            let mut bt: BTreeMap<&str, &Value> = BTreeMap::new();
            for (k, v) in o.iter() {
                bt.insert(k.as_str(), v);
            }

            out.push('{');
            let mut first = true;
            for (k, v) in bt {
                if !first {
                    out.push(',');
                }
                first = false;
                out.push_str(&serde_json::to_string(k).unwrap());
                out.push(':');
                canon_value(out, v);
            }
            out.push('}');
        }
    }
}

fn canon_json(mut v: Value) -> String {
    normalize_negative_zero(&mut v);
    let mut out = String::new();
    canon_value(&mut out, &v);
    out.push('\n');
    out
}

fn main() {
    let mut args = std::env::args().skip(1);
    let cmd = args.next().unwrap_or_default();

    if cmd == "canon" {
        let s = args.next().expect("missing json");
        let v = parse_strict(&s).unwrap_or_else(|e| {
            eprintln!("{}", e);
            std::process::exit(10);
        });
        print!("{}", canon_json(v));
        return;
    }

    if cmd == "canon-file" {
        let path = args.next().expect("missing file");
        let txt = fs::read_to_string(path).unwrap();
        let v: Value = serde_json::from_str(&txt).unwrap();

        if let Some(inp) = v.get("input_json") {
            let vv = parse_strict(&inp.to_string()).unwrap_or_else(|e| {
                eprintln!("{}", e);
                std::process::exit(10);
            });
            print!("{}", canon_json(vv));
            return;
        }

        if let Some(raw) = v.get("input_json_raw").and_then(|x| x.as_str()) {
            let vv = parse_strict(raw).unwrap_or_else(|e| {
                eprintln!("{}", e);
                std::process::exit(10);
            });
            print!("{}", canon_json(vv));
            return;
        }

        eprintln!("vector missing input_json/input_json_raw");
        std::process::exit(3);
    }

    eprintln!("usage: canon <json> | canon-file <path>");
    std::process::exit(2);
}
