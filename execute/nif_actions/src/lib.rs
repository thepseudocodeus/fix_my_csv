/// NIF Action library
///
/// version: 0.0.4
/// date: 12-19-2025
/// Author: AJ Igherighe | The PseudoCodeus
/// license: GNU AGPL v3.0
///
/// Rust NIF functions implement algorithms to transform input into output for Elixir to orchestration layer.
/// NIF functions wrap internal functions that directly execute transformations. This allows Rust code to be tested in Rust.
///
/// Workflow:
/// Phases:
/// 1. From Binary
/// 2. From Data
/// 3. From Structure
///
/// Revised Approach (12/19/2025):
/// - If file is recoded to UTF-8, ~80% of data problems can be solved.
/// - Then, only need to normalize line endings and other items.
///
/// BINARY
/// 1. Strip BOM
/// 2. Santize bytes
/// 3. Convert to UTF-8
/// 4. Normalize file endings
/// 5. Return repaired binary
///
/// Notes:
/// - Should each be orchestrated individually or export a single higher order function?
///     - Individual approach:
///         - Pro:
///             - Can be tested individually
///             - More efficient
///             - More data at orchestration
///         - Con:
///             - Harder to orchestrate
///             - Less efficient
///             - More code
///     - Single higher order function:
///         - Pro:
///             - More efficient
///             - Less code
///         - Con:
///             - Less data at orchestration
///     - Conclusion:
///       - Use a single higher order function and log each step in Rust
///       - Simplifies Elixir orchestration
///       - Establishes orchestration methodology = each layer is responsible for logging its own steps
// src/lib.rs

use rustler::{Env, Error, Binary, OwnedBinary, ResourceArc};
use encoding_rs::UTF_8;
use std::sync::RwLock;
use tracing::{info, span, Level};

// --- State ---
#[derive(rustler::Resource)]
pub struct CsvContext {
    pub raw_data: RwLock<Vec<u8>>,
}

// Extract operating functions to allow testing
/// Convert to UTF-8
pub fn perform_universal_normalization(bytes: &[u8]) -> (String, String) {
    let (cow, encoding, _had_errors) = encoding_rs::UTF_8.decode(bytes);
    let encoding_name = encoding.name().to_string();
    let normalized = cow.replace("\r\n", "\n").replace("\r", "\n");
    (normalized, encoding_name)
}

/// Remove control characters
pub fn perform_noise_cleanup(text: &str) -> String {
    text.chars()
        .filter(|&c| c == '\n' || c == '\t' || !c.is_control())
        .collect()
}

// --- Elixir Interface ---

/// Initialize context
#[rustler::nif]
pub fn init_context<'a>(_env: Env<'a>, input: Binary) -> Result<ResourceArc<CsvContext>, Error> {
    let _ = tracing_subscriber::fmt::try_init();

    let context = CsvContext {
        raw_data: RwLock::new(input.as_slice().to_vec()),
    };

    info!(size = input.len(), "CSV Context Initialized");
    Ok(ResourceArc::new(context))
}

/// Repair and Normalize file data
#[rustler::nif]
pub fn repair_and_normalize<'a>(env: Env<'a>, resource: ResourceArc<CsvContext>) -> Result<Binary<'a>, Error> {
    // Use .read().unwrap() to access the data inside the RwLock
    let raw_bytes = resource.raw_data.read().unwrap();
    let original_size = raw_bytes.len();

    let span = span!(Level::INFO, "repair_pipeline");
    let _enter = span.enter();

    let (normalized, enc) = perform_universal_normalization(&raw_bytes);
    let cleaned = perform_noise_cleanup(&normalized);
    let final_bytes = cleaned.as_bytes();

    info!(
        original_encoding = enc,
        bytes_before = original_size,
        bytes_after = final_bytes.len(),
        "Repair Complete"
    );

    let mut binary = OwnedBinary::new(final_bytes.len())
        // Rustler 0.30+ requires Error strings to be Boxed when using RaiseTerm
        .ok_or(Error::RaiseTerm(Box::new("Memory allocation error")))?;

    binary.as_mut_slice().copy_from_slice(final_bytes);

    Ok(Binary::from_owned(binary, env))
}

#[cfg(test)]
mod tests {
    use super::*;

    #[test]
    fn test_cross_platform_line_endings() {
        let windows_data = b"id,name\r\n1,test\r\n";
        let (normalized, _) = perform_universal_normalization(windows_data);
        assert!(!normalized.contains('\r'), "Should remove carriage returns");
        assert_eq!(normalized, "id,name\n1,test\n");
    }

    #[test]
    fn test_noise_cancellation() {
        let dirty_text = "name\t\u{0000}age";
        let cleaned = perform_noise_cleanup(dirty_text);
        assert!(cleaned.contains('\t'), "Should preserve tabs");
        assert!(!cleaned.contains('\u{0000}'), "Should remove null bytes");
    }

    #[test]
    fn test_idempotency() {
        // Once clean should remain so
        let first_pass = perform_noise_cleanup("clean_text");
        let second_pass = perform_noise_cleanup(&first_pass);
        assert_eq!(first_pass, second_pass);
    }
}

// Ensure matches Elixir Module
rustler::init!("Elixir.Orchestrate");
