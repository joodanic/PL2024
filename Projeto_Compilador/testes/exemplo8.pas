program TesteNot;
var
    x, y: boolean;
    a, b: integer;
begin
    x := not true;
    if x then
        writeln('Teste 1 Falhou')
    else
        writeln('Teste 1 Passou');

    y := not x;
    if y then
        writeln('Teste 2 Passou')
    else
        writeln('Teste 2 Falhou');

    a := 5;
    b := 5;
    x := not (a = b);
    if x then
        writeln('Teste 3 Falhou')
    else
        writeln('Teste 3 Passou');

    x := not 0;
    if x then
        writeln('Teste 4 Passou')
    else
        writeln('Teste 4 Falhou');
end.