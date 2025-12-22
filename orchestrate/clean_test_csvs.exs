#!/usr/bin/env elixir

# Require dependents
Application.ensure_all_started(:orchestrate)

# File.cd!("orchestrate")
# Code.require_file("lib/orchestrate.ex")

input_path =
  IO.gets("📂 Enter the csv directory (or press Enter for current): ")
  |> String.trim()

directory =
  if input_path == "" do
    File.cwd!()
  else
    Path.expand(input_path)
  end

# Find CSV files
# files = Path.wildcard("../test_csvs/*.csv")

# If exist, proceed
if Enum.dir?(directory) do
  # Create list of all csv files
  files =
    directory
    # look in subdirectories
    |> Path.join("**/*.csv")
    |> Path.wildcard()
    |> Enum.filter(fn file ->
      # Handle cases
      Path.extname(file) |> String.downcase() == ".csv"
    end)
    |> Enum.reject()
else
  IO.puts("error: Directory '#{directory}' does not exist")
  System.halt(1)
end

IO.puts("🔍 Found #{length(files)} CSV files\n")

# Clean each file
Enum.each(files, fn file ->
  IO.write("Cleaning #{Path.basename(file)}... ")

  case Orchestrate.clean_csv_file(file) do
    {:ok, stats} ->
      IO.puts("✅ Done!")
      IO.puts("   → #{stats.output}")
      IO.puts("   → Removed #{stats.bytes_removed} bytes\n")

    {:error, reason} ->
      IO.puts("❌ Failed: #{inspect(reason)}\n")
  end
end)

IO.puts("✨ All done!")
