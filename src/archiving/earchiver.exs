defmodule ArchiveCompressor do
  @moduledoc """
  A module to create tar.zst archives with maximum Zstandard compression.
  """

  @doc """
  Creates a compressed tarball (.tar.zst) from a source path to a destination file.
  """
  def create_max_compression_archive(source_path, destination_file) do
    timestamp = DateTime.utc_now() |> DateTime.to_unix()

    destination_file = "#{destination_file}"

    tar_cmd = ["tar", "-cf", "-", source_path]
    zstd_cmd = ["zstd", "--ultra", "-22", "-T0", "-o", destination_file, "-"]

    IO.puts("Starting archival and compression...")

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

ArchiveCompressor.create_max_compression_archive("./my_source_folder", "./archive.tar.zst")
