#!/usr/bin/env elixir

# File.cd!("orchestrate")
Code.require_file("lib/orchestrate.ex")

# Find CSV files
files = Path.wildcard("../test_csvs/*.csv")

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
