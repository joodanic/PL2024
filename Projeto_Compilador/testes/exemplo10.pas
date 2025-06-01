program ContaPalavras;

var
  frase: string;
  i, contador: integer;
  dentroPalavra: boolean;

begin
  writeln('Digite uma frase:');
  readln(frase);

  contador := 0;
  dentroPalavra := False;

  for i := 1 to length(frase) do
  begin
    if (frase[i] <> ' ') then
    begin
      if not dentroPalavra then
      begin
        dentroPalavra := True;
        contador := contador + 1;
      end;
    end
    else
      dentroPalavra := False;
  end;

  writeln('Numero de palavras: ', contador);
end.
