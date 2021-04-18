from django.shortcuts import render
from .Finder import *
import json
import pymongo
from pymongo import MongoClient
import dns
from django.http import HttpResponse
from django.http import JsonResponse
from django.views.decorators.csrf import csrf_exempt
from bson.json_util import dumps
from bson.objectid import ObjectId

#finder_instance = None

#def init(self):
 #       self.finder_instance = Finder()
        
def createConnection():
   return pymongo.MongoClient("mongodb+srv://dbUser:system@cluster0.5hlez.mongodb.net/Finder?retryWrites=true&w=majority")

# Create your views here.
def home(self):
   myclient = createConnection(self)
   mydb = myclient["Finder"]
   mycol = mydb["curriculo"]

   myquery = { "nome": "arthur cardoso" }

   mydoc = mycol.find(myquery)

   for x in mydoc:
      print(x)

   return HttpResponse("Welcome to poll's index!")

def searchByCargo(self):
   client = createConnection(self)
   mydb = client["Finder"]
   mycol = mydb["curriculo"]

   myquery = { "Exp.cargo" : "tecnico" } 

   mydoc = mycol.find(myquery)

   return HttpResponse(mydoc)

@csrf_exempt
def buscarPorVaga(request,VagaID):

   if request.method == 'GET':
      # Inicia conexão com o banco
      client = createConnection()

      mydb = client["Finder"]
      curriculos = mydb["Inscrito"]
      vagas = mydb["vagas"]


      print(VagaID)
      # Recupera a vaga recebida por parâmatro
      vaga = vagas.find_one({"_id" : ObjectId(VagaID)})

      if vaga:
         searchRequisitos = '|'.join([str(requisito['descricao']) for requisito in vaga['competencia']])

         query = {
            "$or" : [ 
               # { "tipoContratoDesejadoInscrito" : { "$regex": vaga['tipoContratacaoPerfilVaga'] } },
               { "perfilProfissionalTituloInscrito" : { "$regex":searchRequisitos } },
               { "perfilProfissionalDescricaoInscrito" : { "$regex": searchRequisitos } },
               { "experienciaProfissional.descricao": { "$regex": searchRequisitos } },
               { "formacao.curso": { "$regex": searchRequisitos } },
               { "competencia.descricao": { "$regex": searchRequisitos } } 
            ] 
         }

         result_curriculos = curriculos.find(query)

         if result_curriculos:
            IdCol = [str(result['_id']) for result in result_curriculos]
            return JsonResponse({
                                 "candidatos" : IdCol,
                                 "message" : ""
                              })
         else:
            return JsonResponse({
                                 "candidatos" : [],
                                 "message" : "Nenhum candidato encontrado para esta vaga."
                              }, status=200)
      else:
         return JsonResponse({"message" : "Vaga não encontrada"}, status=200)
   else:
      return JsonResponse({"message": "Erro na requisição. Método esperado GET."}, status=500)
