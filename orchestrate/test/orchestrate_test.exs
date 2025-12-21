defmodule OrchestrateTest do
  use ExUnit.Case
  doctest Orchestrate

  test "greets the world" do
    assert Orchestrate.hello() == :world
  end

  test "complete heal: handles Windows CRLF, Null bytes, and UTF-8" do
    dirty_input = "id,name\r\n1,Pseudo\0Codeus\r\n"
    result = Orchestrate.clean_csv(dirty_input)
    expected = "id,name\n1,PseudoCodeus\n"
    assert result == expected
  end
end
