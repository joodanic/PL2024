program ContaPalavrasComFuncao;

function ContarPalavras(s: string): integer;
var
  i, total: integer;
  dentroPalavra: boolean;
begin
  total := 0;
  dentroPalavra := False;

  for i := 1 to Length(s) do
  begin
    if s[i] <> ' ' then
    begin
      if not dentroPalavra then
      begin
        dentroPalavra := True;
        total := total + 1;
      end;
    end
    else
      dentroPalavra := False;
  end;

  ContarPalavras := total;
end;

var
  frase: string;
begin
  writeln('Digite uma frase:');
  readln(frase);

  writeln('Numero de palavras: ', ContarPalavras(frase));
end.
