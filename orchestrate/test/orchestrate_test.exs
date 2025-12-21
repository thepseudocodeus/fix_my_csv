defmodule OrchestrateTest do
  use ExUnit.Case
  doctest Orchestrate

  test "complete heal: handles Windows CRLF, Null bytes, and UTF-8" do
    dirty_input = "id,name\r\n1,Pseudo\0Codeus\r\n"
    result = Orchestrate.clean_csv(dirty_input)
    expected = "id,name\n1,PseudoCodeus\n"
    assert result == expected
  end

  test "normalizes Windows line endings (CRLF)" do
    input = "id,name\r\n1,test\r\n"
    result = Orchestrate.clean_csv(input)
    assert result == "id,name\n1,test\n"
    refute String.contains?(result, "\r")
  end

  test "normalizes old Mac line endings (CR only)" do
    input = "id,name\r1,test\r"
    result = Orchestrate.clean_csv(input)
    assert result == "id,name\n1,test\n"
  end

  test "removes null bytes" do
    input = "hello\0world"
    result = Orchestrate.clean_csv(input)
    assert result == "helloworld"
  end

  test "preserves tabs and newlines" do
    input = "col1\tcol2\nval1\tval2\n"
    result = Orchestrate.clean_csv(input)
    assert result == "col1\tcol2\nval1\tval2\n"
  end

  test "handles empty input" do
    result = Orchestrate.clean_csv("")
    assert result == ""
  end

  test "preserves valid UTF-8 characters" do
    input = "héllo,wörld\nñoño,café\n"
    result = Orchestrate.clean_csv(input)
    assert result == "héllo,wörld\nñoño,café\n"
  end

  test "removes control characters but keeps tabs and newlines" do
    input = "hello\x01\x02world\ttab\nnewline"
    result = Orchestrate.clean_csv(input)
    assert result == "helloworld\ttab\nnewline"
  end

  test "handles mixed line endings in same file" do
    input = "line1\r\nline2\rline3\nline4"
    result = Orchestrate.clean_csv(input)
    assert result == "line1\nline2\nline3\nline4"
  end

  test "doctest example: remove_null_bytes_nil" do
    result = Orchestrate.remove_null_bytes_nil("hi\0 y'all")
    assert result == "hi y'all"
  end

  test "real-world CSV with multiple issues" do
    input =
      "ID,Name,Status\r\n" <>
        "1,Test\0User,Active\r\n" <>
        "2,Café\x01Owner,Pending\r" <>
        "3,José,Complete\n"

    result = Orchestrate.clean_csv(input)

    expected =
      "ID,Name,Status\n" <>
        "1,TestUser,Active\n" <>
        "2,CaféOwner,Pending\n" <>
        "3,José,Complete\n"

    assert result == expected
  end

  test "handles binary input type" do
    input = <<104, 101, 108, 108, 111, 0, 119, 111, 114, 108, 100>>
    result = Orchestrate.clean_csv(input)
    assert result == "helloworld"
  end
end
