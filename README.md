#  Plataforma de Streaming de vídeos
Projeto universitário para a Universidade Autónoma de Lisboa no âmbito da unidade curricular Arquitétura Avançada de Sistemas.   

Este projeto é uma plataforma de streaming básica com funcionalidades de adicionar video, remover video, editar video e tambem fazer o streaming do video.   

Os videos têm que conter um título, uma thumnail e um video .mp4. Ainda podem conter uma descrição, sendo que esta é opcional.
Na tela inicial da plataforma, os videos são organizados por "views", onde os mais populares aparecem primeiro e os menos pupolares aparecem em último.
A adição, remoção e edição dos videos é feita no painel de administrador.
Na edição dos videos pode'se mudar o nome, descrição, thumbnail e o video .mp4.

## Linguagens usadas no projeto
- Python - usada para o backend da plataforma;
- HTML - usada para fazer o frontend;
- CSS - usada para fazer o design do frontend;
- JavaScript - usada para fazer a interligação entre o frontend e o backend.

Neste projeto ainda foi usado o Docker com os Kubernetes para simular vários serviços em diferentes máquinas.  

Para base de dados foi usado o MongoDB que armazena o título, descrição, o nome do ficheiro da thumnail, o nome do ficheiro do video, duração do video e as views do video.  

A thumbgnail e o video são armazenados num container do Docker.  
