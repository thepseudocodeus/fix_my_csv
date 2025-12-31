use std::env;
use std::error::Error;
use std::fs::File;
use std::io::{self, BufReader};
use std::path::PathBuf;
use walkdir::WalkDir;

fn main() {
    let start_dir = "test_csvs";
    let base_path = "test_csvs/test1.csv";
    // let current_dir = env::current_dir();
    let current_dir = env::current_dir().expect("Failed to get current directory");
    println!("Current working directory: {}", current_dir.display());
    // let test_file = format!("{}/{}", &current_dir.expect("REASON").display(), base_path);
    let test_file = current_dir.join(base_path);
    println!("Full path: {}", test_file.display());

    if !test_file.exists() {
        eprintln!("File does not exist: {}", test_file.display());
        return;
    }
    // println!("File Locations: {test_file}");
    // let result = validate_with_csv(test_file);
    // println!("Result: {result:?}");
    if let Err(err) = validate_with_csv(&test_file.to_string_lossy()) {
        eprintln!("Validation Error: {err}");
    }

    let files = index_files(start_dir);
    println!("Files: {files:?}");
}

fn index_files(start_dir: &str) -> io::Result<Vec<PathBuf>> {
    // Create a container for data
    let mut files: Vec<PathBuf> = Vec::new();

    for entry_result in WalkDir::new(start_dir) {
        let entry = match entry_result {
            Ok(entry) => entry,
            Err(err) => {
                eprintln!("Error reading directory entry: {err}");
                continue; // Skip problematic entries
            }
        };

        let metadata = match entry.metadata() {
            Ok(metadata) => metadata,
            Err(err) => {
                eprintln!("Error getting metadata for entry: {err}");
                continue;
            }
        };

        if metadata.is_file() {
            let file_path = entry.path().to_path_buf();
            files.push(file_path);
        }
    }
    Ok(files)
}

// Approach #1: Use CSV to validate
// Notes:
// - https://docs.rs/csv/1.1.6/csv/
// - Ensure csv crate is installed
fn validate_with_csv(file_path: &str) -> Result<(), Box<dyn Error>> {
    let f = File::open(file_path)?;
    let buf_rdr = BufReader::new(f);
    // let mut rdr = csv::Reader::from_reader(BufReader::new(f));
    let mut rdr = csv::ReaderBuilder::new()
        .has_headers(false)
        .from_reader(buf_rdr);

    for result in rdr.records() {
        let record = result?;
        println!("{:?}", record);
    }
    println!("File is valid.");
    Ok(())
}
