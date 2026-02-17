use std::process;

fn usage() -> ! {
    eprintln!("isc_verify");
    eprintln!("Usage:");
    eprintln!("  isc_verify --version");
    eprintln!("  isc_verify <bundle_path>");
    process::exit(2);
}

fn main() {
    let mut args = std::env::args().skip(1);

    match args.next().as_deref() {
        Some("--version") | Some("-V") => {
            println!("{}", env!("CARGO_PKG_VERSION"));
        }
        Some(path) => {
            println!("bundle_path={}", path);
        }
        None => usage(),
    }
}