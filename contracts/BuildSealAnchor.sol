// SPDX-License-Identifier: MIT
pragma solidity ^0.8.20;

/// @title BuildSealAnchor
/// @notice Minimal anchor contract for BuildSeal checkpoints (Merkle roots).
///         Designed for L2 usage (Base/Polygon/Arbitrum).
/// @dev Verifiers read the Anchored event to confirm merkleRoot inclusion.
contract BuildSealAnchor {
    /// @notice Emitted when a Merkle root is anchored.
    /// @param merkleRoot The batch Merkle root (bytes32).
    /// @param batchId Monotonic or arbitrary batch identifier chosen by the caller/system.
    /// @param metaHash Optional metadata hash (e.g., hash of batch manifest); can be zero.
    /// @param sender The caller who anchored.
    /// @param blockNumber The block number at anchoring time (for convenience).
    event Anchored(
        bytes32 indexed merkleRoot,
        uint64 indexed batchId,
        bytes32 metaHash,
        address indexed sender,
        uint256 blockNumber
    );

    /// @notice Anchor a Merkle root.
    /// @dev No access control in v1; governance can be layered later via separate contracts.
    ///      If you need allow-listing, deploy behind a permissioned forwarder.
    function anchor(bytes32 merkleRoot, uint64 batchId, bytes32 metaHash) external {
        require(merkleRoot != bytes32(0), "ZERO_ROOT");
        emit Anchored(merkleRoot, batchId, metaHash, msg.sender, block.number);
    }
}
