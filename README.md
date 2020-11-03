# Segmentador de sementes
Segmentador convertido de java para python

## Como rodar

- É necessário ter python 3.6  ou superior instalado, e também o pip, gerenciador de pacotes python
- Crie um ambiente virtual para isnstalar as libs com o comando ``` python3 -m venv venv```
- após ative o ambiente utilizando o comando ```source /venv/bin/activate```
- instale as libs necessárias com o comando  ```pip install -e requirements.txt```
- rode o programa utilizando python3 main.py

### parâmetros opcionais para rodar o programa

Podem ser utilizado os seguintes parâmetros opcionais

- --img para especificar a pasta de imagens a ser utilizada.
- --save para salvar ou não as imagens intermediárias.
- --ruido para setar o valor mínimo de área a ser considerado

### Exemplo de código para rodar com os parâmetros
``python main.py --save --img /imgs/sementes --ruido 10``