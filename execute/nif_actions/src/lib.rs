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
use rustler::{Env, Error, Binary, OwnedBinary, ResourceArc};
use encoding_rs::UTF_8;
use std::sync::RwLock;
use tracing::{info, warn, span, Level};

// --- State ---
pub struct CsvContext {
    pub raw_data: RwLock<Vec<u8>>,
    pub processed_text: RwLock<String>,
}

// --- Cross Platform Interop ---
impl CsvContext {
    /// Normalizes across Windows, Mac, and Linux to UTF-8 and Unix Line Endings (\n)
    fn universal_normalize(bytes: &[u8]) -> (String, String) {
        // Transcode to UTF-8
        let (cow, encoding, _had_errors) = encoding_rs::UTF_8.decode(bytes);
        let encoding_name = encoding.name().to_string();

        // Normalize Line Endings to '\n (Unix)
        let normalized = cow.replace("\r\n", "\n").replace('\r', "\n");

        (normalized, encoding_name)
    }
}

// --- NIF Interface for Elixir ---
#[rustler::nif]
pub fn init_context<'a>(env: Env<'a>, input: Binary) -> Result<ResourceArc<CsvContext>, Error> {
    // Initialize logging subscriber once if not already done
    let _ = tracing_subscriber::fmt::try_init();

    let context = CsvContext {
        raw_data: RwLock::new(input.as_slice().to_vec()),
        processed_text: RwLock::new(String::new()),
    };

    info!(size = input.len(), "CSV Context Initialized");
    Ok(ResourceArc::new(context))
}

#[rustler::nif]
pub fn repair_and_normalize<'a>(env: Env<'a>, resource: ResourceArc<CsvContext>) -> Result<Binary<'a>, Error> {
    let raw_bytes = resource.raw_data.read().unwrap();
    let original_size = raw_bytes.len();

    let span = span!(Level::INFO, "repair_pipeline");
    let _enter = span.enter();

    let (normalized, enc) = CsvContext::universal_normalize(&raw_bytes);

    let cleaned: String = normalized.chars()
        .filter(|&c| c == '\n' || c == '\t' || !c.is_control())
        .collect();

    let final_bytes = cleaned.as_bytes();

    info!(
        original_encoding = enc,
        bytes_before = original_size,
        bytes_after = final_bytes.len(),
        reduction_ratio = format!("{:.4}", final_bytes.len() as f64 / original_size as f64),
        "Repair Complete"
    );

    let mut binary = OwnedBinary::new(final_bytes.len())
        .ok_or(Error::RaiseTerm("Memory allocation error"))?;
    binary.as_mut_slice().copy_from_slice(final_bytes);

    Ok(Binary::from_owned(binary, env))
}

#[cfg(test)]
mod tests {
    use super::*;

    #[test]
    fn test_cross_platform_line_endings() {
        // Resolve Windows line endings
        let windows_data = b"id,name\r\n1,test\r\n";
        let (normalized, _) = CsvContext::universal_normalize(windows_data);

        // \r and \n should remain
        assert!(!normalized.contains('\r'));
        assert!(normalized.contains('\n'));
        assert_eq!(normalized, "id,name\n1,test\n");
    }

    #[test]
    fn test_noise_cancellation() {
        let dirty_data = "name\t\u{0000}age".as_bytes();
        let (normalized, _) = CsvContext::universal_normalize(dirty_data);

        let cleaned: String = normalized.chars()
            .filter(|&c| c == '\n' || c == '\t' || !c.is_control())
            .collect();

        assert!(cleaned.contains('\t'));
        assert!(!cleaned.contains('\u{0000}'));
    }

    #[test]
    fn test_encoding() {
        // Remove null byte
        let dirty_data = "name\t\u{0000}age".as_bytes();
        let (normalized, encoding) = CsvContext::universal_normalize(dirty_data);
        assert_eq!(encoding, "UTF-8");
    }
}

// --- Send to Elixir ---
rustler::init!("Elixir.Orchestrate");
