/// NIF Action library
///
/// version: 0.1.0
/// date: 12-20-2025
/// Author: AJ Igherighe | The PseudoCodeus
/// license: GNU AGPL v3.0
///
/// Provides CSV data cleaning and normalization via Rust NIFs.
/// Handles encoding conversion, line ending normalization, and control character sanitization.

use rustler::{Env, Error, Binary, OwnedBinary};
use tracing::{info, span, Level};

// --- Core Transformation Functions ---

/// Strips BOM and transcodes to UTF-8, normalizing line endings
fn normalize_encoding_and_line_endings(bytes: &[u8]) -> (String, String) {
    let (cow, encoding, _had_errors) = encoding_rs::UTF_8.decode(bytes);
    let encoding_name = encoding.name().to_string();

    // Normalize all line endings to Unix-style \n
    let normalized = cow
        .replace("\r\n", "\n")
        .replace('\r', "\n");

    (normalized, encoding_name)
}

/// Removes null bytes and control characters (preserving \n and \t)
fn sanitize_control_chars(text: &str) -> String {
    text.chars()
        .filter(|&c| c == '\n' || c == '\t' || !c.is_control())
        .collect()
}

/// Main transformation pipeline
fn repair_csv_binary(bytes: &[u8]) -> (String, String) {
    let (normalized, encoding_name) = normalize_encoding_and_line_endings(bytes);
    let sanitized = sanitize_control_chars(&normalized);
    (sanitized, encoding_name)
}

// --- NIF Interface ---

#[rustler::nif]
pub fn repair_and_normalize<'a>(
    env: Env<'a>,
    input: Binary
) -> Result<Binary<'a>, Error> {
    let _ = tracing_subscriber::fmt::try_init();

    let span = span!(Level::INFO, "csv_repair");
    let _enter = span.enter();

    let original_size = input.len();
    let (cleaned_text, detected_encoding) = repair_csv_binary(input.as_slice());
    let final_bytes = cleaned_text.as_bytes();

    info!(
        original_encoding = detected_encoding,
        bytes_before = original_size,
        bytes_after = final_bytes.len(),
        reduction_ratio = format!("{:.4}", final_bytes.len() as f64 / original_size as f64),
        "CSV repair complete"
    );

    let mut binary = OwnedBinary::new(final_bytes.len())
        .ok_or_else(|| Error::RaiseTerm(Box::new("Memory allocation failed")))?;

    binary.as_mut_slice().copy_from_slice(final_bytes);
    Ok(Binary::from_owned(binary, env))
}

// Send to Elixir
rustler::init!("Elixir.Orchestrate");

// --- Tests ---

#[cfg(test)]
mod tests {
    use super::*;

    #[test]
    fn test_windows_line_endings() {
        let input = b"id,name\r\n1,test\r\n";
        let (result, _) = repair_csv_binary(input);
        assert_eq!(result, "id,name\n1,test\n");
        assert!(!result.contains('\r'));
    }

    #[test]
    fn test_old_mac_line_endings() {
        let input = b"id,name\r1,test\r";
        let (result, _) = repair_csv_binary(input);
        assert_eq!(result, "id,name\n1,test\n");
    }

    #[test]
    fn test_removes_null_bytes() {
        let input = b"hello\0world";
        let (result, _) = repair_csv_binary(input);
        assert_eq!(result, "helloworld");
    }

    #[test]
    fn test_preserves_tabs_and_newlines() {
        let input = b"col1\tcol2\nval1\tval2\n";
        let (result, _) = repair_csv_binary(input);
        assert_eq!(result, "col1\tcol2\nval1\tval2\n");
    }


    #[test]
    fn test_empty_input() {
        let (result, _) = repair_csv_binary(b"");
        assert_eq!(result, "");
    }

    #[test]
    fn test_utf8_detection() {
        let input = "héllo,wörld\n".as_bytes();
        let (result, encoding) = repair_csv_binary(input);
        assert_eq!(encoding, "UTF-8");
        assert_eq!(result, "héllo,wörld\n");
    }

    #[test]
    fn test_removes_control_characters() {
        let input = b"hello\x01\x02world";
        let (result, _) = repair_csv_binary(input);
        assert_eq!(result, "helloworld");
    }
}
