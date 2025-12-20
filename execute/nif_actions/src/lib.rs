use rustler::{Env, Error, Binary, OwnedBinary};
use std::borrow::Cow;
// use rustler::NifResult;

/// Removes null bytes from string
// fn remove_null_bytes(input: String) -> String {
//     // Replaces null bytes with empty string
//     // Notes:
//     // - To test, moved core functionality into this private function
//     input.replace("\0", "")
// }

/// Remove null bytes from binary
#[rustler::nif]
pub fn remove_null_bytes_nif<'a>(env: Env<'a>, input: Binary) -> Result<Binary<'a>, Error> {
    let cleaned: Vec<u8> = input.as_slice().iter().copied().filter(|&b| b != 0).collect();
    let mut binary = OwnedBinary::new(cleaned.len())
        .ok_or(Error::RaiseTerm("Failed to allocate binary"))?;
    binary.as_mut_slice().copy_from_slice(&cleaned);
    Ok(Binary::from_owned(binary, env))
}

// #[rustler::nif]
// pub fn remove_null_bytes_nif(input: String) -> String {
//     remove_null_bytes(&input)
// }

/// Remove control characters but retain tab, newline, and carriage returns
/// Note: Windows and legacy MacOs can use unsupported characters
// fn sanitize_csv_string(input: String) -> String {
//     // Iterate through characters
//     input.chars()
//         .filter(|&c| {
//             matches!(c, '\t' | '\n' | '\r') ||
//             (c >= ' ' && c <= '~') ||
//             c as u32 >= 0x80 // [] TODO: Add rust documentation section on why this is needed for UTF-8
//         })
//         .collect()
// }

/// Remove control characters except tab, newline, carriage return
#[rustler::nif]
pub fn sanitize_csv_binary_nif<'a>(env: Env<'a>, input: Binary) -> Result<Binary<'a>, Error> {
    let cleaned = sanitize_bytes(input.as_slice());
    let mut binary = OwnedBinary::new(cleaned.len())
        .ok_or(Error::RaiseTerm("Failed to allocate binary"))?;
    binary.as_mut_slice().copy_from_slice(&cleaned);
    Ok(Binary::from_owned(binary, env))
}


// ----------------------------------------------------------------------------
// Binary Helpers
// ----------------------------------------------------------------------------
fn sanitize_bytes(bytes: &[u8]) -> Vec<u8> {
    bytes.iter().copied()
        .filter(|&b| matches!(b, 0x09 | 0x0A | 0x0D | 0x20..=0x7E) || b >= 0x80)
        .collect()
}

fn strip_bom(bytes: &[u8]) -> &[u8] {
    if bytes.starts_with(&[0xEF, 0xBB, 0xBF]) { &bytes[3..] }
    else if bytes.starts_with(&[0xFF, 0xFE]) || bytes.starts_with(&[0xFE, 0xFF]) { &bytes[2..] }
    else { bytes }
}

fn normalize_line_endings_cow(input: &str) -> Cow<str> {
    if input.contains("\r") || input.contains("\n") {
        Cow::Owned(input.replace("\r\n", "\n").replace('\r', "\n").replace('\n', "\r\n"))
    } else {
        Cow::Borrowed(input)
    }
}


// ----------------------------------------------------------------------------
// Tests
// ----------------------------------------------------------------------------
#[cfg(test)]
mod tests {
    use super::*;

    #[test]
    fn test_remove_null_bytes() {
        assert_eq!(remove_null_bytes("hi\0, no \0nulls".to_string()), "hi, no nulls");
        assert_eq!(remove_null_bytes("never had nulls".to_string()), "never had nulls");
    }

    #[test]
    fn test_keep_normal_ascii_characters() {
        // This should now keep all characters expected.
        let input = "This is a test. Normal ASCII.";
        let output = sanitize_csv_string(input.to_string());
        assert_eq!(output, "This is a test. Normal ASCII.");
    }

    #[test]
    fn test_remove_control_characters_except_tab_newline_cr() {
        let input = "Hi\x00\tThere\n\x07CR\r";
        let output = sanitize_csv_string(input.to_string());
        assert_eq!(output, "Hi\tThere\nCR\r");
    }

    #[test]
    fn test_keep_utf8_characters() {
        let input = "Café 漢字 Привет"; // Should not be removed
        let output = sanitize_csv_string(input.to_string());
    }

    #[test]
    fn removes_del_character() {
        let input = format!("Hello{}World", 0x7Fu8 as char);
        let output = sanitize_csv_string(input);
        assert_eq!(output, "HelloWorld");
    }

    #[test]
    fn keeps_tabs_newlines_and_carriage_returns() {
        let input = "a\tb\nc\rd";
        let output = sanitize_csv_string(input.to_string());
        assert_eq!(output, "a\tb\nc\rd");
    }

    #[test]
    fn removes_all_other_controls() {
        // Control Char Ranges = 0x01–0x08, 0x0B–0x0C, 0x0E–0x1F
        let bad_chars: String = (1u8..=31)
            .filter(|&b| !matches!(b, b'\t' | b'\n' | b'\r'))
            .map(|b| b as char)
            .collect();
        let input = format!("Good{}Bad", bad_chars);
        let output = sanitize_csv_string(input);
        assert_eq!(output, "GoodBad");
    }
}


rustler::init!("Elixir.Orchestrate");
