program WrongReturnType;
function TestFunc(x: integer): integer;
begin
  TestFunc := 'abc';
end;
begin
  writeln(TestFunc(5));
end.