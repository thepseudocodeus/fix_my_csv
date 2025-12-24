defmodule ArchiveCompressor do
  @moduledoc """
  A module to create tar.zst archives with maximum Zstandard compression.
  """

  @doc """
  Creates a compressed tarball (.tar.zst) from a source path to a destination file.

  Uses Zstandard level 22 (maximum compression) with the --ultra flag.
  The script pipes the tar output to zstd.

  ## Examples
      ArchiveCompressor.create_max_compression_archive(
        "/path/to/source_directory",
        "/path/to/archive.tar.zst"
      )
  """
  def create_max_compression_archive(source_path, destination_file) do
    timestamp = DateTime.utc_now() |> DateTime.to_unix()

    destination_file = "#{destination_file}"

    # Command 1: Create a tar archive and write to stdout (-)
    tar_cmd = ["tar", "-cf", "-", source_path]
    # Command 2: Compress stdin (-) with zstd max level and write to output file
    # The --ultra flag is required for levels > 19
    zstd_cmd = ["zstd", "--ultra", "-22", "-T0", "-o", destination_file, "-"]

    IO.puts("Starting archival and compression...")

    # Execute the tar command and pipe its output to the zstd command
    tar_process =
      System.cmd(List.first(tar_cmd), List.delete_at(tar_cmd, 0),
        stderr_to_stdout: true,
        into: :pipe
      )

    case tar_process do
      {tar_output, 0} ->
        # If tar succeeds, pipe its output through zstd
        zstd_process =
          System.cmd(List.first(zstd_cmd), List.delete_at(zstd_cmd, 0),
            stdin: tar_output,
            stderr_to_stdout: true
          )

        case zstd_process do
          {zstd_output, 0} ->
            IO.puts("Successfully created max compression archive: #{destination_file}")
            {:ok, destination_file}

          {zstd_output, status} ->
            IO.puts("Zstd compression failed with status #{status}. Output/Error: #{zstd_output}")
            {:error, :zstd_failure, zstd_output}
        end

      {tar_output, status} ->
        IO.puts("Tar command failed with status #{status}. Error: #{tar_output}")
        {:error, :tar_failure, tar_output}
    end
  end
end

# To run this from a script:
# Ensure you have tar and zstd installed and available in your system's PATH.
#
# Example usage:
# elixir earchiver

ArchiveCompressor.create_max_compression_archive("./my_source_folder", "./archive.tar.zst")
