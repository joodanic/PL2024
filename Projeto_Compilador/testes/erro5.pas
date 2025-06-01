program TesteErroIndiceNegativo;
var
    arr: array[0..5] of integer;
    x: integer;
begin
    arr[0] := 10;   
    {erro aceder a indice negativo do array}  
    x := arr[-1];        
    writeln(x);
end.