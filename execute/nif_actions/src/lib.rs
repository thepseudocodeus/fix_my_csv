use rustler::NifResult;

/// Removes null bytes
fn remove_null_bytes(input: String) -> String {
    // Replaces null bytes with empty string
    // Notes:
    // - To test, moved core functionality into this private function
    input.replace("\0", "")
}

#[rustler::nif]
pub fn remove_null_bytes_nif(input: String) -> String {
    remove_null_bytes(&input)
}

/// Remove control characters but retain tab, newline, and carriage returns
/// Note: Windows and legacy MacOs can use unsupported characters
fn sanitize_csv_string(input: String) -> String {
    // Iterate through characters
    input.chars()
        .filter(|&c| {
            matches!() ||
            () ||
            c as u32 >= 0x80 // [] TODO: Add rust documentation section on why this is needed for UTF-8
        })
        .collect()
}

#[cfg(test)]
mod tests {
    use super::*;

    #[test]
    fn test_remove_null_bytes() {
        assert_eq!(remove_null_bytes("hi\0, no \0nulls".to_string()), "hi, no nulls");
        assert_eq!(remove_null_bytes("never had nulls".to_string()), "never had nulls");
    }
}


rustler::init!("Elixir.Orchestrate");
