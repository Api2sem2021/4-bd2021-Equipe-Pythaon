
import json
import pymongo
import dns

from .Finder import *

from pymongo import MongoClient

from django.shortcuts import render
from django.http import HttpResponse
from django.http import JsonResponse
from django.views.decorators.csrf import csrf_exempt

from bson import ObjectId
from bson.json_util import dumps
from bson.objectid import ObjectId
from datetime import datetime
import time

        
def createConnection():
   # return pymongo.MongoClient("mongodb+srv://dbUser:system@cluster0.5hlez.mongodb.net/Finder?retryWrites=true&w=majority")
   return pymongo.MongoClient("mongodb://localhost:27017")

@csrf_exempt
def buscarvaga(request, pk):
   if request.method == "GET":
      client = createConnection()
      db = client["Finder"]
      col = db["vagas"]
  
      vaga = col.find_one({"VagaIdExterno" : pk})
      
      if vaga:
         return JsonResponse(json.loads(dumps(vaga)), safe=False)
      else:
         return JsonResponse({"message" : "Vaga não encontrada."}, status=200)
   else:
      return JsonResponse({"message": "Erro na requisição. Método esperado: GET."}, status=500)
  
@csrf_exempt
def insert_vaga(request):
   if request.method == "POST":
      client = createConnection()
      db = client["Finder"]
      col = db["vagas"]
      
      result = col.insert_one(json.loads(request.body))
      # result
      return JsonResponse({"message" : "Vaga cadastrada com sucesso."}, status=200)
   else:
      return JsonResponse({"message": "Erro na requisição. Método esperado: POST."}, status=500)

@csrf_exempt
def updatevaga(request, id):
   if request.method == "PUT":
      client = createConnection()
      db = client["Finder"]
      col = db["vagas"]

      result = col.update_one({"VagaIdExterno" : id}, json.loads(request.body))
      # result
      return JsonResponse({"message":"Vaga atualizada com sucesso."}, status=200)
   else:
      return JsonResponse({"message":"Erro na requisição. Método esperado: PUT."}, status=500)  

@csrf_exempt
def delete_vaga(request, pk):
   if request.method == "DELETE":
      client = createConnection()
      db = client["Finder"]
      col = db["vagas"]

      result = col.delete_many({"VagaIdExterno": pk})
      # result
      return JsonResponse({"message":"Vaga excluída com sucesso."}, status=200)
   else:
      return JsonResponse({"message":"Erro na requisição. Método esperado: DELETE."}, status=500) 

@csrf_exempt
def buscarCurriculo(request, pk):
   if request.method == 'GET':
      client = createConnection()
      db = client["Finder"]
      curriculos = db["Inscrito"]

      curriculo = curriculos.find_one({"InscritoIdExterno": pk})

      if curriculo:
         return JsonResponse(json.loads(dumps(curriculo)), safe=False)
      else:
         return JsonResponse({"message" : "Currículo não encontrado."}, status=200, safe=False)
   else:
      return JsonResponse({"message": "Erro na requisição. Método esperado: GET."}, status=500, safe=False)

@csrf_exempt
def cadastrarCurriculo(request):
   if request.method == "POST":
      client = createConnection()         
      db = client["Finder"]
      col = db["Inscrito"]

      result = col.insert_one(json.loads(request.body))
      # result
      return JsonResponse({"message":"Currículo inserido com sucesso."}, status=200)
   else:
      return JsonResponse({"message":"Erro na requisição. Método esperado: POST."}, status=500) 

@csrf_exempt
def atualizarCurriculo(request, pk):
   if request.method == "PUT":
      client = createConnection()
      db = client["Finder"]
      col = db["Inscrito"]

      result = col.update_one({"InscritoIdExterno" : pk}, json.loads(request.body))
      # result
      return JsonResponse({"message":"Currículo atualizado com sucesso."}, status=200)
   else:
      return JsonResponse({"message":"Erro na requisição. Método esperado: PUT."}, status=500)   

@csrf_exempt
def deletarCurriculo(request, pk):
   if request.method == "DELETE":
      client = createConnection()
      db = client["Finder"]
      col = db["Inscrito"]

      result = col.delete_many({"InscritoIdExterno" : pk})
   # result
      return JsonResponse({"message" : "Currículo excluído com sucesso."}, status=200)
   else:
      return JsonResponse({"message" : "Erro na requisição. Método esperado: DELETE."}, status=500)   

@csrf_exempt
def buscarPorVaga(request,VagaID):
   if request.method == 'GET':
      # Inicia conexão com o banco
      client = createConnection()

      mydb = client["Finder"]
      curriculos = mydb["Inscrito"]
      vagas = mydb["vagas"]

      # Recupera a vaga recebida por parâmetro
      # vaga = vagas.find_one({"InscritoIdExterno" : ObjectId(VagaID)})
      vaga = vagas.find_one({"InscritoIdExterno" : VagaID})

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
            IdCol = [str(result['InscritoIdExterno']) for result in result_curriculos]
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
      return JsonResponse({"message": "Erro na requisição. Método esperado: GET."}, status=500)
   
@csrf_exempt
def buscaFiltrada(request):
   if request.method == 'GET':
      client = createConnection()
      mydb = client["Finder"]
      curriculos = mydb["Inscrito"]
      parametros = json.loads(request.body)
      query = {}
      
      try:
         for item in parametros:
            if isinstance(item, dict):
               if item['tipo'] == 'texto':
                  if isinstance(item['valor'], list): query[item['chave']] = { "$regex": '(?i)' + '|'.join([str(requisito) for requisito in item['valor']])  }
                  else: query[item['chave']] = { "$regex": '(?i)' + item['valor'] }
               elif item['tipo'] == 'distancia': 
                  query[item['chave']] = {
                        "$near" : {
                           "$geometry"    : { "type": "Point",  "coordinates": item['valor'] },
                           "$minDistance" : item['mindist'],
                           "$maxDistance" : item['maxdist']
                        }
                  }
               elif item['tipo'] == 'data':
                  if 'eq'  in item: query[item['chave']] = { "$eq" : item['eq'] }
                  if 'ne'  in item: query[item['chave']] = { "$ne" : item['ne'] }
                  if 'gt'  in item: query[item['chave']] = { "$gt" : item['gt'] }
                  if 'gte' in item: query[item['chave']] = { "$gte" : item['gte'] }
                  if 'lt'  in item: query[item['chave']] = { "$lt" : item['lt'] }
                  if 'lte' in item: query[item['chave']] = { "$lte" : item['lte'] }
                  # if 'in'  in item: query[item['chave']] = { "$in" : item['in'] }
                  # if 'nin' in item: query[item['chave']] = { "$nin" : item['nin'] } 
            else:
               return JsonResponse({"message": "Parâmetros inválidos."}, status=500)
         print(query)
         data = time.time()
         curriculos = curriculos.find(query)
         print("Tempo de execução: ",time.time() - data)
      except:
         return JsonResponse({"message": "Erro ao gerar a busca. Os parâmetros enviados contém erros."}, status=500)
      
      return JsonResponse(json.loads(dumps(curriculos)), safe=False)
   else:
      return JsonResponse({"message": "Erro na requisição. Método esperado: GET."}, status=500)
   