import requests
from sonarqube_api import SonarAPIHandler
from flask import Flask, request
from flask_restful import Resource, Api

app = Flask(__name__)
api = Api(app)
#create an object to call all the api functionalities by providing valid
#user name and password
ref = SonarAPIHandler(user='admin',password='admin',host='http://10.26.32.107')

#make http-get call to get components('name of the projects','key of the projects', etc.) of all the projects.
comp = ref._make_call(method='get',endpoint='/api/projects/index')
ex_comp = comp.json()
projectkeys = set()
for p in ex_comp:
   projectkeys.add(p['k'])


#get all projects listed
class get_project_list(Resource):
   def get(self):
      extract_json = comp.json()
      project = []
      co=1 
      for p in extract_json:
	 dict={}
         dict["Project_Name_"+str(co)] = p['nm']
	 co=co+1	 
         project.append(dict)
      return {'Project_Count':len(extract_json),'Projects':project}

#get key of a project by passing the name of the project
class get_project_key(Resource):
   def get(self,projectName):
      extract_json=comp.json()
      for p in extract_json:
         if p['nm']==projectName:
            return {'Key':(p['k'])}

#get status of all projects -> OK, ERROR, WARN
class get_project_status_all(Resource):
   def get(self):
   
      extract_json = comp.json()
      project=[]
	  
      for p in extract_json:
         res = ref._make_call(method='get', endpoint='/api/qualitygates/project_status?projectKey='+str(p['k']))
         dict = {}
         dict['Project_Name']=str(p['nm'])
         dict['Project_Status']=str(res.json()['projectStatus']['status'])
         project.append(dict)
		 
      return {'Projects':project}

#get status of a particular project by passing the key of the that project
class get_project_status(Resource):
   def get(self,projectKey):
      if str(projectKey) not in projectkeys:
        return {'Error_in_key':404}

      res = ref._make_call(method='get', endpoint='/api/qualitygates/project_status?projectKey='+str(projectKey))
      res_ex = res.json()
      return {'Project_status': str(res_ex['projectStatus']['status'])}

#get issues counts of all the projects
class get_project_issues_open_all(Resource):
   def get(self):
      extract_json=comp.json()
      project=[]

      for p in extract_json:
         dict={}
         dict['Project_Name'] = str(p['nm'])
         issue_raw = ref._make_call(method='get', endpoint='/api/issues/search?facets=severities&resolved=false&componentKeys='+str(p['k']))
         issue_json = issue_raw.json()

         for e in issue_json['facets']:
            for ee in e['values']:
               dict[str(ee['val'])]=str(ee['count'])
         project.append(dict)
      return {'Projects':project}

#get issues counts of a particular project by passing the key of that project

class get_issues_closed_all(Resource):
   def get(self):
      extract_json = comp.json()
      project = []
      
      for p in extract_json:
         dict={}
         dict['Project_Name'] = str(p['nm'])
         issue_raw = ref._make_call(method='get', endpoint='/api/issues/search?facets=severities&resolved=true&componentKeys='+str(p['k']))
         issue_json = issue_raw.json()

         for e in issue_json['facets']:
            for ee in e['values']:
               dict[str(ee['val'])]=str(ee['count'])
         project.append(dict)
      return {'Projects': project}


class get_project_issues_open(Resource):
   def get(self,projectKey):
      dict={}
      issue_raw = ref._make_call(method='get', endpoint='/api/issues/search?facets=severities&resolved=false&componentKeys='+str(projectKey))
      issue_json=issue_raw.json()
      if projectKey not in projectkeys:
         return {'Invalid_key':404}

      extract_json = comp.json()
      for p in extract_json:
         if p['k']==projectKey:
            projectName=p['nm']
            break
      
      dict['Project_Name']=projectName
     # print('Count of the issue Severity: ')
      for e in issue_json['facets']:
         for ee in e['values']:
            dict[str(ee['val'])]=str(ee['count'])

      return {'Issue_count ':dict}

class get_issues_closed(Resource):
   def get(self,projectKey):
      dict={}
      issue_raw = ref._make_call(method='get', endpoint='/api/issues/search?facets=severities&resolved=true&componentKeys='+str(projectKey))
      issue_json=issue_raw.json()
      if projectKey not in projectkeys:
         return {'Invalid_key':404}

      extract_json = comp.json()
      for p in extract_json:
         if p['k']==projectKey:
            projectName=p['nm']
            break

      dict['Project_Name']=projectName
     # print('Count of the issue Severity: ')
      for e in issue_json['facets']:
         for ee in e['values']:
            dict[str(ee['val'])]=str(ee['count'])

      return {'Issue_count ':dict}

      
       
api.add_resource(get_project_list,'/projectList')
api.add_resource(get_project_key,'/projectKey/<string:projectName>')
api.add_resource(get_project_status_all,'/projectStatusAll')
api.add_resource(get_project_status,'/projectStatus/<string:projectKey>')
api.add_resource(get_project_issues_open_all,'/projectIssuesOpenAll')
api.add_resource(get_project_issues_open,'/projectIssuesOpen/<string:projectKey>')
api.add_resource(get_issues_closed_all,'/projectIssuesClosedAll')
api.add_resource(get_issues_closed,'/projectIssuesClosed/<string:projectKey>')
if __name__=='__main__':
   app.run(debug=True, host='10.26.34.190', port='9000')


