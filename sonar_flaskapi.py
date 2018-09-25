import requests
from sonarqube_api import SonarAPIHandler
from flask import Flask, request
from flask_restful import Resource, Api
from flask_cors import CORS, cross_origin

app = Flask(__name__)
CORS(app)
api = Api(app)


#create an object to call all the api functionalities by providing valid
#user name and password
ref = SonarAPIHandler(user='admin',password='admin',host='http://10.26.32.107')

#make http-get call to get components('name of the projects','key of the projects', etc.) of all the projects.
comp = ref._make_call(method='get',endpoint='/api/projects/index')
ex_comp = comp.json()

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
   def get(self,projectName):
      extract_json = comp.json()
      for p in extract_json:
         if str(projectName) == p['nm']:
            projectKey = str(p['k'])
            break
      res = ref._make_call(method='get', endpoint='/api/qualitygates/project_status?projectKey='+projectKey)
      res_ex = res.json()
      return {'Project_status': str(res_ex['projectStatus']['status'])}

#get issues counts of all the projects

class get_project_issues_open_all(Resource):
   def get(self):
      extract_json=comp.json()
      project=[]
      dict_issues = {}
      blocko=0
      minoro=0
      majoro=0
      crto=0
      infoo=0
      co=0
      for p in extract_json:
         co=co+1
         dict_issues['Project_Name'] = str(p['nm'])
         issue_raw = ref._make_call(method='get', endpoint='/api/issues/search?facets=severities&resolved=false&componentKeys='+str(p['k']))
         issue_json = issue_raw.json()

         for e in issue_json['facets']:
            for ee in e['values']:
               dict_issues[str(ee['val'])]=str(ee['count'])
               if str(ee['val']) == "MINOR":
                  minoro+=int(dict_issues[str(ee['val'])])
               elif str(ee['val'])=="MAJOR":
                  majoro+=int(dict_issues[str(ee['val'])])
               elif str(ee['val'])=="CRITICAL":
                  crto+=int(dict_issues[str(ee['val'])])    
               elif str(ee['val'])=="INFO":
                  infoo+=int(dict_issues[str(ee['val'])])
               elif str(ee['val'])=="BLOCKER":
                  blocko+=int(dict_issues[str(ee['val'])])
         project.append(dict_issues)
      return {'Count_Projects':co,'Open_Issues_list':project,'MINOR_Issues_Total':minoro,'MAJOR_Issues_Total':majoro,'CRITICAL_Issues_Total':crto,'INFO_Issues_Total':infoo,'BLOCKER_Issues_Total':blocko }

#get issues counts of a particular project by passing the key of that project

class get_issues_all(Resource):
   def get(self):
      extract_json = comp.json()
      project = []
      project1 = []
      co=0
      block=0   
      minor=0
      major=0
      crt=0
      info=0
      dict_issues = {}
      blocko=0
      minoro=0
      majoro=0
      crto=0
      infoo=0

      for p in extract_json:
         dict_issues={}
         dict_issues['Project_Name'] = str(p['nm'])
         issue_raw = ref._make_call(method='get', endpoint='/api/issues/search?facets=severities&resolved=false&componentKeys='+str(p['k']))
         issue_json = issue_raw.json()

         for e in issue_json['facets']:
            for ee in e['values']:
               dict_issues[str(ee['val'])]=str(ee['count'])
               if str(ee['val']) == "MINOR":
                  minoro+=int(dict_issues[str(ee['val'])])
               elif str(ee['val'])=="MAJOR":
                  majoro+=int(dict_issues[str(ee['val'])])
               elif str(ee['val'])=="CRITICAL":
                  crto+=int(dict_issues[str(ee['val'])])
               elif str(ee['val'])=="INFO":
                  infoo+=int(dict_issues[str(ee['val'])])
               elif str(ee['val'])=="BLOCKER":
                  blocko+=int(dict_issues[str(ee['val'])])

         project1.append(dict_issues)
      
      ext_json = comp.json() 
      for pp in ext_json:
         dict={}
         dict['Project_Name'] = str(pp['nm'])
         issue_raw = ref._make_call(method='get', endpoint='/api/issues/search?facets=severities&resolved=true&componentKeys='+str(pp['k']))
         issue_json = issue_raw.json()
         co=co+1
    
         for e in issue_json['facets']:
            for ee in e['values']:
               dict[str(ee['val'])]=str(ee['count'])
               if str(ee['val']) == "MINOR":
                  minor+=int(dict[str(ee['val'])])
               elif str(ee['val'])=="MAJOR":
                  major+=int(dict[str(ee['val'])])
               elif str(ee['val'])=="CRITICAL":
                  crt+=int(dict[str(ee['val'])])
               elif str(ee['val'])=="INFO":
                  info+=int(dict[str(ee['val'])])
               elif str(ee['val'])=="BLOCKER":
                  block+=int(dict[str(ee['val'])])
         project.append(dict)
        

      return {'Pro_Closed_Issues_list': project,'Pro_Open_issues_list':project1,'Count_Projects':co, 'MAJOR_Issues_Total_closed':major, 'MINOR_Issues_Total_closed':minor, 'CRITICAL_Issues_Total_closed':crt, 'INFO_Issues_Total_closed':info, 'BLOCKER_Issues_Total_closed':block,'MAJOR_Issues_Total_open':majoro, 'MINOR_Issues_Total_open':minoro, 'CRITICAL_Issues_Total_open':crto, 'INFO_Issues_Total_open':infoo, 'BLOCKER_Issues_Total_open':blocko}


class get_project_issues_open(Resource):
   def get(self,projectName):
      dict={}
      extract_json = comp.json()
      for p in extract_json:
         if str(projectName)==p['nm']:
           projectKey = str(p['k'])
           break
      issue_raw = ref._make_call(method='get', endpoint='/api/issues/search?facets=severities&resolved=false&componentKeys='+str(projectKey))
      issue_json=issue_raw.json()
     
      extract_json = comp.json()
      for p in extract_json:
         if p['k']==projectKey:
            projectName1=p['nm']
            break
      
      dict['Project_Name']=projectName1
     # print('Count of the issue Severity: ')
      for e in issue_json['facets']:
         for ee in e['values']:
            dict[str(ee['val'])]=str(ee['count'])

      return {'Issue_count ':dict}

class get_issues_closed(Resource):
   def get(self,projectName):
      dict={}
      extract_json = comp.json()
      
      for p in extract_json:
         if str(projectName)==p['nm']:
           projectKey=str(p['k'])
           break
      issue_raw = ref._make_call(method='get', endpoint='/api/issues/search?facets=severities&resolved=true&componentKeys='+str(projectKey))
      issue_json=issue_raw.json()

      extract_json = comp.json()
      for p in extract_json:
         if p['k']==projectKey:
            projectName1=p['nm']
            break

      dict['Project_Name']=projectName1
     # print('Count of the issue Severity: ')
      for e in issue_json['facets']:
         for ee in e['values']:
            dict[str(ee['val'])]=str(ee['count'])

      return {'Issue_count ':dict}

      
       
api.add_resource(get_project_list,'/projectList')
api.add_resource(get_project_key,'/projectKey/<string:projectName>')
api.add_resource(get_project_status_all,'/projectStatusAll')
api.add_resource(get_project_status,'/projectStatus/<string:projectName>')
api.add_resource(get_project_issues_open_all,'/projectIssuesOpenAll')
api.add_resource(get_project_issues_open,'/projectIssuesOpen/<string:projectName>')
api.add_resource(get_issues_all,'/projectIssuesAll')
api.add_resource(get_issues_closed,'/projectIssuesClosed/<string:projectName>')
if __name__=='__main__':
   app.run(debug=True, host='10.26.34.190', port='9000')


