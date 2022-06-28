Search.setIndex({docnames:["auto-review","client","concepts","config","dataset-type","datasets","docextract","docextract-intro","docextract_settings","document-report-ex","document_report","document_report_types","examples","exports","filters","graphql-ex","graphql_queries","image-dataset-ex","image-predictions-ex","index","intro","jobs","jobs-type","migration","model-group-type","model-type","model_groups","model_predictions","object-detection","ocr-object-parse-ex","review-intro","singleocr-ex","storage","submission-ex","submissions","train-predict-ex","training-progress","user-metrics-ex","user-metrics-types","user_metrics","workflow","workflow-ex","workflow-intro","workflow-metrics","workflow-metrics-ex","workflow-metrics-types"],envversion:{"sphinx.domains.c":2,"sphinx.domains.changeset":1,"sphinx.domains.citation":1,"sphinx.domains.cpp":5,"sphinx.domains.index":1,"sphinx.domains.javascript":2,"sphinx.domains.math":2,"sphinx.domains.python":3,"sphinx.domains.rst":2,"sphinx.domains.std":2,sphinx:56},filenames:["auto-review.rst","client.rst","concepts.rst","config.rst","dataset-type.rst","datasets.rst","docextract.rst","docextract-intro.rst","docextract_settings.rst","document-report-ex.rst","document_report.rst","document_report_types.rst","examples.rst","exports.rst","filters.rst","graphql-ex.rst","graphql_queries.rst","image-dataset-ex.rst","image-predictions-ex.rst","index.rst","intro.rst","jobs.rst","jobs-type.rst","migration.rst","model-group-type.rst","model-type.rst","model_groups.rst","model_predictions.rst","object-detection.rst","ocr-object-parse-ex.rst","review-intro.rst","singleocr-ex.rst","storage.rst","submission-ex.rst","submissions.rst","train-predict-ex.rst","training-progress.rst","user-metrics-ex.rst","user-metrics-types.rst","user_metrics.rst","workflow.rst","workflow-ex.rst","workflow-intro.rst","workflow-metrics.rst","workflow-metrics-ex.rst","workflow-metrics-types.rst"],objects:{"indico.client":[[1,0,0,"-","client"]],"indico.client.client":[[1,1,1,"","IndicoClient"]],"indico.client.client.IndicoClient":[[1,2,1,"","call"]],"indico.config":[[3,0,0,"-","config"]],"indico.config.config":[[3,1,1,"","IndicoConfig"]],"indico.filters":[[14,0,0,"-","__init__"]],"indico.filters.__init__":[[14,1,1,"","SubmissionFilter"]],"indico.queries":[[5,0,0,"-","datasets"],[6,0,0,"-","documents"],[13,0,0,"-","export"],[21,0,0,"-","jobs"],[26,0,0,"-","model_groups"],[32,0,0,"-","storage"],[34,0,0,"-","submission"],[40,0,0,"-","workflow"]],"indico.queries.datasets":[[5,1,1,"","AddDatasetFiles"],[5,1,1,"","CreateDataset"],[5,1,1,"","DeleteDataset"],[5,1,1,"","GetDataset"],[5,1,1,"","GetDatasetFileStatus"],[5,1,1,"","GetDatasetStatus"],[5,1,1,"","ListDatasets"],[5,1,1,"","RemoveDatasetFile"]],"indico.queries.document_report":[[10,1,1,"","GetDocumentReport"]],"indico.queries.documents":[[6,1,1,"","DocumentExtraction"]],"indico.queries.export":[[13,1,1,"","CreateExport"],[13,1,1,"","DownloadExport"],[13,1,1,"","GetExport"]],"indico.queries.jobs":[[21,1,1,"","JobStatus"]],"indico.queries.model_groups":[[26,1,1,"","AddModelGroupComponent"],[26,1,1,"","GetModelGroup"],[26,1,1,"","GetModelGroupSelectedModelStatus"],[26,1,1,"","ModelGroupPredict"]],"indico.queries.storage":[[32,1,1,"","CreateStorageURLs"],[32,1,1,"","RetrieveStorageObject"],[32,1,1,"","UploadDocument"]],"indico.queries.submission":[[34,1,1,"","GenerateSubmissionResult"],[34,1,1,"","GetSubmission"],[34,1,1,"","ListSubmissions"],[34,1,1,"","RetrySubmission"],[34,1,1,"","SubmissionResult"],[34,1,1,"","SubmitReview"],[34,1,1,"","UpdateSubmission"],[34,1,1,"","WaitForSubmissions"]],"indico.queries.usermetrics":[[39,1,1,"","GenerateChangelogReport"],[39,1,1,"","GetUserChangelog"],[39,1,1,"","GetUserSnapshots"],[39,1,1,"","GetUserSummary"]],"indico.queries.workflow":[[40,1,1,"","GetWorkflow"],[40,1,1,"","ListWorkflows"],[40,1,1,"","WorkflowSubmission"]],"indico.queries.workflow_metrics":[[43,1,1,"","GetWorkflowMetrics"]],"indico.types":[[4,0,0,"-","datafile"],[4,0,0,"-","dataset"],[11,0,0,"-","document_report"],[22,0,0,"-","jobs"],[25,0,0,"-","model"],[24,0,0,"-","model_group"],[38,0,0,"-","user_metrics"],[45,0,0,"-","workflow_metrics"]],"indico.types.datafile":[[4,1,1,"","Datafile"]],"indico.types.datafile.Datafile":[[4,3,1,"","deleted"],[4,3,1,"","failure_type"],[4,3,1,"","file_hash"],[4,3,1,"","file_size"],[4,3,1,"","file_type"],[4,3,1,"","id"],[4,3,1,"","name"],[4,3,1,"","num_pages"],[4,3,1,"","page_ids"],[4,3,1,"","pages"],[4,3,1,"","rainbow_url"],[4,3,1,"","status"],[4,3,1,"","status_meta"]],"indico.types.dataset":[[4,1,1,"","DataColumn"],[4,1,1,"","Dataset"],[4,1,1,"","LabelSet"]],"indico.types.dataset.DataColumn":[[4,3,1,"","id"],[4,3,1,"","name"]],"indico.types.dataset.Dataset":[[4,3,1,"","datacolumns"],[4,3,1,"","files"],[4,3,1,"","id"],[4,3,1,"","labelsets"],[4,3,1,"","name"],[4,3,1,"","permissions"],[4,3,1,"","row_count"]],"indico.types.dataset.LabelSet":[[4,3,1,"","id"],[4,3,1,"","name"]],"indico.types.document_report":[[11,1,1,"","DocumentReport"],[11,1,1,"","InputFile"]],"indico.types.jobs":[[22,1,1,"","Job"]],"indico.types.jobs.Job":[[22,3,1,"","id"],[22,3,1,"","ready"],[22,3,1,"","status"]],"indico.types.model":[[25,1,1,"","Model"],[25,1,1,"","TrainingProgress"]],"indico.types.model.Model":[[25,3,1,"","id"],[25,3,1,"","status"],[25,3,1,"","training_progress"]],"indico.types.model.TrainingProgress":[[25,3,1,"","percent_complete"]],"indico.types.model_group":[[24,1,1,"","ModelGroup"]],"indico.types.model_group.ModelGroup":[[24,3,1,"","id"],[24,3,1,"","name"],[24,3,1,"","status"],[24,3,1,"","task_type"]],"indico.types.user_metrics":[[38,1,1,"","AppRoles"],[38,1,1,"","DatasetRole"],[38,1,1,"","UserChangelog"],[38,1,1,"","UserChangelogReport"],[38,1,1,"","UserDatasets"],[38,1,1,"","UserSnapshot"],[38,1,1,"","UserSummary"],[38,1,1,"","UserSummaryCounts"]],"indico.types.user_metrics.AppRoles":[[38,3,1,"","count"],[38,3,1,"","role"]],"indico.types.user_metrics.DatasetRole":[[38,3,1,"","dataset_id"],[38,3,1,"","role"]],"indico.types.user_metrics.UserChangelog":[[38,3,1,"","changes_made"],[38,3,1,"","datasets"],[38,3,1,"","date"],[38,3,1,"","enabled"],[38,3,1,"","id"],[38,3,1,"","previous_datasets"],[38,3,1,"","previous_roles"],[38,3,1,"","previously_enabled"],[38,3,1,"","roles"],[38,3,1,"","updated_by"],[38,3,1,"","updater_email"],[38,3,1,"","user_email"],[38,3,1,"","user_id"]],"indico.types.user_metrics.UserChangelogReport":[[38,3,1,"","job_id"]],"indico.types.user_metrics.UserDatasets":[[38,3,1,"","dataset_id"],[38,3,1,"","role"]],"indico.types.user_metrics.UserSnapshot":[[38,3,1,"","created_at"],[38,3,1,"","datasets"],[38,3,1,"","email"],[38,3,1,"","enabled"],[38,3,1,"","id"],[38,3,1,"","name"],[38,3,1,"","roles"]],"indico.types.user_metrics.UserSummary":[[38,3,1,"","app_roles"],[38,3,1,"","users"]],"indico.types.user_metrics.UserSummaryCounts":[[38,3,1,"","disabled"],[38,3,1,"","enabled"]],"indico.types.workflow_metrics":[[45,1,1,"","ClassStpMetrics"],[45,1,1,"","DailyPredictionMetric"],[45,1,1,"","DailyQueueMetric"],[45,1,1,"","DailyStpMetric"],[45,1,1,"","DailySubmissionMetric"],[45,1,1,"","DailyTimeOnTaskMetric"],[45,1,1,"","ModelStpMetrics"],[45,1,1,"","PredictionMetric"],[45,1,1,"","PredictionMetrics"],[45,1,1,"","QueueMetrics"],[45,1,1,"","StpMetric"],[45,1,1,"","StraightThroughProcessing"],[45,1,1,"","SubmissionMetric"],[45,1,1,"","TimeOnTaskMetric"],[45,1,1,"","TimeOnTaskMetrics"],[45,1,1,"","WorkflowMetrics"],[45,1,1,"","WorkflowMetricsOptions"],[45,1,1,"","WorkflowStpMetrics"]],"indico.types.workflow_metrics.ClassStpMetrics":[[45,3,1,"","aggregate"],[45,3,1,"","class_name"],[45,3,1,"","daily"]],"indico.types.workflow_metrics.DailyPredictionMetric":[[45,3,1,"","num_preds"]],"indico.types.workflow_metrics.DailyQueueMetric":[[45,3,1,"","avg_age_in_queue"],[45,3,1,"","hours_on_queue"],[45,3,1,"","subs_on_queue"]],"indico.types.workflow_metrics.DailyStpMetric":[[45,3,1,"","auto_review_denom"],[45,3,1,"","auto_review_numerator"],[45,3,1,"","auto_review_stp_pct"],[45,3,1,"","date"],[45,3,1,"","review_denom"],[45,3,1,"","review_numerator"],[45,3,1,"","review_stp_pct"]],"indico.types.workflow_metrics.DailySubmissionMetric":[[45,3,1,"","completed"],[45,3,1,"","completed_exception_queue"],[45,3,1,"","completed_in_review"],[45,3,1,"","completed_review_queue"],[45,3,1,"","date"],[45,3,1,"","rejected_in_review"],[45,3,1,"","submitted"]],"indico.types.workflow_metrics.DailyTimeOnTaskMetric":[[45,3,1,"","avg_min_per_doc_exceptions"],[45,3,1,"","avg_mins_per_doc"],[45,3,1,"","avg_mins_per_doc_review"],[45,3,1,"","date"]],"indico.types.workflow_metrics.ModelStpMetrics":[[45,3,1,"","aggregate"],[45,3,1,"","class_metrics"],[45,3,1,"","daily"],[45,3,1,"","model_group_id"],[45,3,1,"","name"]],"indico.types.workflow_metrics.PredictionMetrics":[[45,3,1,"","aggregate"],[45,3,1,"","daily"]],"indico.types.workflow_metrics.StpMetric":[[45,3,1,"","auto_review_denom"],[45,3,1,"","auto_review_numerator"],[45,3,1,"","auto_review_stp_pct"],[45,3,1,"","review_denom"],[45,3,1,"","review_numerator"],[45,3,1,"","review_stp_pct"]],"indico.types.workflow_metrics.StraightThroughProcessing":[[45,3,1,"","model"],[45,3,1,"","workflow"]],"indico.types.workflow_metrics.TimeOnTaskMetric":[[45,3,1,"","avg_min_per_doc_exceptions"],[45,3,1,"","avg_mins_per_doc"],[45,3,1,"","avg_mins_per_doc_review"]],"indico.types.workflow_metrics.TimeOnTaskMetrics":[[45,3,1,"","aggregate"],[45,3,1,"","daily"]],"indico.types.workflow_metrics.WorkflowMetrics":[[45,3,1,"","first_submitted_date"],[45,3,1,"","predictions"],[45,3,1,"","queues"],[45,3,1,"","straight_through_processing"],[45,3,1,"","submissions"],[45,3,1,"","time_on_task"],[45,3,1,"","workflow_id"]],"indico.types.workflow_metrics.WorkflowMetricsOptions":[[45,3,1,"","REIVEW"],[45,3,1,"","STRAIGHT_THROUGH_PROCESSING"],[45,3,1,"","SUBMISSIONS"],[45,3,1,"","TIME_ON_TASK"]],"indico.types.workflow_metrics.WorkflowStpMetrics":[[45,3,1,"","daily"]]},objnames:{"0":["py","module","Python module"],"1":["py","class","Python class"],"2":["py","method","Python method"],"3":["py","attribute","Python attribute"]},objtypes:{"0":"py:module","1":"py:class","2":"py:method","3":"py:attribute"},terms:{"0":[0,6,7,8,21,23,26,28,29,30,31,33,41,44],"0001":30,"1":[9,23,33,37,41,44],"100":[5,16,37,40],"1000":[9,33,34,42],"1234":41,"128x165":8,"14":8,"155":30,"155_etl_output":30,"180m":34,"182":28,"2":[21,23,28,33,37,41,44],"20":5,"2021":[9,44],"221":28,"225":28,"227":28,"231":28,"232":16,"24":30,"256":28,"265":28,"28":[30,44],"2f":36,"3":[0,6,7,8,20,33,37,41,44],"30":34,"30403":27,"30970":18,"314":28,"34":30,"342":16,"386":28,"3a":41,"3b":41,"3c":41,"3e50f5e6":16,"4":[8,28,33,37],"40":30,"400":28,"4137_23703_1582037135":23,"415":28,"423":16,"424e":16,"425":28,"4305":36,"435":28,"439":28,"440":28,"4567":41,"480":28,"5":[26,33,37],"5000":28,"52":30,"5751668214797974":28,"5e":28,"5x":[6,7,8],"6":[20,44],"60":34,"618":28,"6826":[41,44],"7":[8,9,20,37],"70c5":16,"731":30,"7589":42,"8":20,"8231":42,"9064":16,"921":23,"99":30,"9fba12b5ba17":16,"boolean":34,"break":29,"byte":4,"case":[7,16,23,27,30,41,42],"char":8,"class":[1,3,4,5,6,7,10,11,13,14,19,21,22,23,24,25,26,32,34,35,38,39,40,41,43,45],"default":[3,5,8,13,20,21,34,43],"do":[0,2,7,17,27,33],"export":19,"final":[30,42],"float":[21,25,34,45],"function":[2,6,7,8,42],"import":[0,7,9,15,17,18,20,23,28,29,30,31,33,35,36,37,41,42,44],"int":[4,5,6,13,16,21,22,24,25,26,34,38,39,40,41,43,45],"long":38,"new":[2,12,20,23,26,27,41,42],"return":[1,3,5,6,7,8,13,14,16,18,21,22,26,30,32,34,40,42,43,44],"true":[0,3,5,6,7,8,13,16,17,21,23,26,27,28,29,30,31,33,34,35,37,38,40,41,42],"try":28,"while":[2,5,30,35],A:[2,4,8,11,15,24,25,30,32,34,38,41,42],And:[16,37],Be:23,By:[3,8],For:[2,6,23,28,42],If:[1,2,3,8,16,20,21,27,28,32,34,42],In:[0,2,7,8,16,23,28,30,42],It:[7,8,24],NOT:[6,34],One:[2,13,24],The:[0,1,2,3,4,5,7,8,17,18,20,23,24,25,27,28,29,30,34,36,38,42,45],Then:33,There:[7,17,28,44],These:8,To:[0,5,20,27,28,42],Will:6,With:[1,17,19,21,27,28,42],__init__:14,__version__:20,_no_valu:0,abil:42,abl:[0,28,30],about:[4,11,20,28,38,39,42,45],abov:[8,16,17,20,28,30,42],ac:28,accept:[32,33,42,45],access:[16,17,29,38],account:38,across:45,action:30,activ:24,actual:[2,3,41],ad:[7,8,26,41],add:[0,5,8,26],add_classes_filt:41,add_data:23,add_extract:41,add_group:41,add_linked_label_transform:41,adddatasetfil:5,addit:[2,7,8,30,41],addition:8,addlinkclassificationcompon:41,addlinkedlabelcompon:41,addmodelgroupcompon:[26,28,35,41],address:30,admin:30,admin_review:30,administr:16,after:[0,21,28,30,38,41,42],after_component_id:[26,28,41],afterward:20,ag:45,aggreg:[44,45],airlin:[27,35],airline_com:35,aka:12,alert:42,all:[0,2,5,6,7,8,13,15,20,27,30,33,34,38,40,42,44],all_pr:23,all_submiss:10,allow:[0,20],along:[16,42],alongsid:28,alreadi:[28,30],also:[0,2,7,8,16,20,21,23,24,30,41,42],altern:[7,42],alternate_ocr:8,alwai:[1,8,27,30],amount:45,an:[2,3,4,6,7,8,13,16,17,20,21,22,26,27,28,31,32,33,34,35,37,41,42,44],analysi:37,ani:[0,2,8,32,33,34],annot:28,anonym:13,anoth:20,anyth:8,anytim:2,api:[0,3,7,16,17,18,23,28,31,33,35,37],api_kei:23,api_token:3,api_token_path:[1,3,9,15,17,18,20,23,27,29,31,33,35,36,37,41,44],app:[3,9,15,16,17,18,20,29,30,31,33,35,36,37,38,39,41,42,44],app_rol:[37,38],appear:[0,8,42],append:29,appli:42,applic:[7,20,27,30,45],approl:38,appropri:1,approv:[0,30],ar:[0,2,3,4,6,7,8,16,17,18,22,24,25,27,28,30,32,33,37,38,42,44,45],aren:16,argument:[0,8,26],around:16,arriv:42,articl:42,ask:2,assign:[2,16,38,39,42],associ:[2,4,5,8,11,26,41,42,44],assum:7,asynchron:[21,22,42],attribut:[3,8,21,30,34,38,44,45],authent:[34,40],author:8,auto:[19,30,33,34,42,45],auto_review_denom:45,auto_review_numer:45,auto_review_stp_pct:45,automat:[0,23,28,42],avail:[0,2,7,8,16,21,26,37,38],averag:45,avg_age_in_queu:45,avg_min_per_doc_except:45,avg_mins_per_doc:45,avg_mins_per_doc_review:45,await:30,back:[39,41,45],background_color:8,base:[8,16,30,39,45],basic:[7,8],batch:[5,6],batch_siz:[5,28],bb:8,bbbot:8,bbleft:8,bbright:8,bbtop:8,becom:34,been:[4,23,28,30,33,42,44],befor:[0,30,34,42],begin:42,behavior:6,being:30,below:[0,2,6,16,17,18,23,27,28,29,30,42],best:[23,24],better:27,between:[8,23],bewar:8,bit:20,block:[5,6,7,12],block_index:8,block_offset:8,block_typ:8,blue:20,bold:8,bool:[3,4,5,13,14,16,21,22,34,38],both:[2,7,8,20],bottom:[8,28],bound:[6,8,28],boundari:8,box:[6,8,28],browser:20,bufferediobas:32,build:37,built:16,bundl:40,button:[20,24],by_kei:41,bypass:34,calcul:8,call:[0,1,2,6,7,15,17,18,22,23,28,29,30,31,32,33,35,36,37,41,42,44],can:[0,2,7,8,16,18,20,21,24,26,27,28,29,30,32,34,36,37,38,41,42,43],cancel:27,cannot:34,capabl:7,captur:28,care:23,categor:27,cautiou:42,ce5364a:28,cell:8,certain:[8,42],certif:3,chang:[0,30,33,34,37,38],changelog:[37,38],changes_mad:38,charact:[6,7],check:[12,30,33,34,44],check_statu:34,choos:7,circl:28,class_id:41,class_metr:45,class_nam:45,classif:[2,8,41,42],classifi:[12,27,42],classstpmetr:45,click:[0,2,20,24,30,42],client:[0,1,2,6,7,9,15,16,17,18,22,27,28,29,30,31,33,35,36,37,41,42,44],close:8,code:[16,17,23,28,29],col_end:8,col_start:8,collect:[2,20,23],color:8,column:[8,13,17,26,28,35],column_id:13,column_nam:41,com:[3,20,23,27,33],combin:[13,23],combine_label:13,come:39,comment:[27,35],common:19,commun:[8,20],compani:[16,20],complet:[5,13,14,21,23,24,25,26,30,31,33,34,35,36,44,45],completed_exception_queu:45,completed_in_review:45,completed_review_queu:45,compon:[26,41],component_by_typ:[26,28,41],comput:[8,17,28],concept:[19,23],confid:[7,28,30],config:[1,3,9,15,17,18,20,23,27,29,31,33,35,36,37,41,44],configu:20,configur:[1,3,6,16,23,29,43],confirm:0,consist:8,constructor:[3,20],consult:23,contain:[0,2,4,7,8,14,17,24,26,28,37,42],content:[8,32],continu:[2,37],control:20,cool:[33,34],copi:[0,26,27],core:2,corner:[8,27],correct:2,cost:8,costli:27,could:42,count:[38,39,43],counterpart:8,creat:[2,5,12,13,14,15,16,20,23,24,25,26,28,30,31,33,35,37,41,42],create_model_request:28,created_at:38,created_at_end_d:9,created_at_start_d:9,createdataset:[5,16,17,23,28,35],createexport:13,createmodelgroup:23,createstorageurl:32,createworkflow:[28,41],creation:38,creationd:8,creator:8,criteria:[0,39],critic:30,csv:[2,13,16,17,23,28,35,37,39],csv_column_name_of_urls_or_path:28,cumul:45,current:[0,2,24,28],custom:[0,7,23,26,30,42],d:[16,30],dai:[20,37,39,44,45],daili:[43,44,45],daily_cumul:45,dailypredictionmetr:45,dailyqueuemetr:45,dailystpmetr:45,dailysubmissionmetr:45,dailytimeontaskmetr:45,dashboard:20,data:[2,6,7,8,13,16,17,18,23,24,26,27,28,35,37,38,42,43,44],datacolumn:[4,16,41],datacolumn_by_nam:[23,28,35,41],datacolumn_id:41,datafil:[4,5,13],datafilepag:4,datafram:[17,44],dataset:[0,12,13,15,16,19,23,26,30,35,38,40,41,42,44],dataset_id:[5,13,23,26,28,35,38,40,41,44],dataset_typ:5,datasetrol:38,datasetspag:16,date:[9,37,38,39,43,44,45],datetim:[9,37,38,39,43,44],debugg:44,delet:[4,5,16],deletedataset:[5,16],demonstr:[7,17,29,30,42],departur:23,depend:17,desc:34,descend:34,describ:[20,26,42],descript:[5,20],design:0,detail:[6,7,23,39,42,43],detect:[8,19],develop:20,df:44,dict:[3,6,8,14,16,21,31,32,33,34],dictionari:[0,3,7,8],did:[27,34,37],differ:[18,20,25,42],dimens:8,directli:16,directori:[3,7,20],disabl:[38,39,45],disclosur:42,disk:32,distinguish:23,doc:20,doc_index:8,doc_offset:8,document:[5,6,7,12,16,18,19,20,23,30,32,33,41,42,45],document_report:[9,10,11],document_titl:8,documentextract:[12,16,19,22,23,29,32],documentreport:[9,11],documentreportfilt:9,doe:[1,3,7,8],domain:[16,23],don:28,done:33,doucment:29,down:[7,8],download:[5,13,20,38],downloadexport:13,ducment:45,e:[2,7,8,16,28,32],each:[0,7,8,24,27,28,30,42],earliest:45,easier:20,easili:42,easilli:42,edit:30,effici:20,either:[2,7,8,20,21,28,32],element:28,elif:33,els:[0,33],email:[37,38],empti:[0,44],enabl:[0,30,33,37,38,39,42,45],encapsul:42,encount:4,encrypt:8,end:[8,30,37,39,43],end_dat:[37,39,43,44],engin:7,entri:[8,38],env:7,environ:[1,3],equal:[0,30,42],equival:16,error:[1,4,16,21,30,33],essenti:41,etc:28,etl_output:30,even:[0,27,30],everi:[2,8],exact:[7,8],exampl:[0,6,7,8,9,10,13,16,19,27,28,29,30,33,37,41,42,44],except:[0,30,34,45],exclus:8,exist:[1,3,41],expir:27,explain:[2,18],explor:20,export_id:13,extend:[9,37],extract:[2,6,7,8,16,32,41,42],extracted_data:6,extracted_fil:[7,29,31],extraction_model:41,extrem:[6,20],f:[33,36],fail:[2,5,13,14,24,25,26,30,33,34,35],failur:[4,22],failure_typ:4,fals:[3,5,8,10,13,16,17,23,26,28,30,33,34,40],far:27,fast:[6,7,8],faster:[6,7,8],featur:0,fetch:[12,38],few:[2,23,27],field:[8,30,42],file:[0,2,3,4,5,6,7,12,14,16,17,18,20,23,28,29,30,32,33,34,35,37,38,40,42],file_hash:4,file_id:5,file_info:13,file_s:4,file_typ:4,fileinput:16,filemeta:28,filenam:[5,32],filepath:32,files:8,files_to_extract:[7,29],filetyp:4,fill:0,filter:[9,10,19,30,33,34,37,39,40,41],filter_empti:28,filter_opt:[9,37],filtered_class:41,financi:42,financial_doc:23,financial_docu:23,financial_stat:23,find:[2,16,20,23,30,41,42],finetunecollect:23,finish:[5,16,18,23,30,34],first:[8,18,28,30,41,42],first_submitted_d:45,five:[7,8],fix:30,flag:[0,14],flexibl:[20,23,42],flight:27,flyer:27,follow:[0,2,7,8,16,20,30,41,42],font:[7,8],font_siz:8,force_complet:34,force_rend:8,form_extract:41,format:[6,7,8,16,17,28,39],former:8,formextract:32,found:[16,26,34,36,40,41,42],four:6,frequent:27,from:[0,2,3,5,6,7,8,9,12,13,15,16,20,23,25,26,27,28,29,30,31,33,35,36,37,41,42,44],from_local_imag:[5,17,28],frozen:13,frozen_labelset_id:13,full:[8,16,20,29,37],full_document_text:29,further:32,g:[8,16,32],gap:8,gather:18,gener:[10,18,19,20,23,26,30,33,34,37,45],generatechangelogreport:[37,39],generatesubmissionresult:[30,34],get:[5,7,8,12,13,16,19,26,27,28,29,30,35,36,37,41],getdataset:[5,16,41],getdatasetfilestatu:5,getdatasetstatu:5,getdocumentreport:[9,10],getexport:13,getmodelgroup:[16,26,36],getmodelgroupselectedmodelstatu:[26,35],getsubmiss:[30,34,42],gettrainingmodelwithprogress:36,getuserchangelog:[37,39],getusersnapshot:[37,39],getusersummari:[37,39],getworkflow:[40,41],getworkflowmetr:[43,44],give:20,given:[0,7,26,30,34,42],go:30,got:[8,27],graph:[16,20,37],graphql:[1,12,19],graphqlrequest:[1,15],great:20,group:[16,19,23,25,27,36,41,45],group_1:41,ha:[3,4,21,23,30,33,38,42,44],had:23,handl:[8,16,22,23],hard:33,hasn:30,have:[3,7,8,23,28,30,33,34,38,42,44],header:8,height:8,help:23,here:[7,16,17,20,27,37,42],hex:8,highli:7,hold:[2,27],home:[3,7,20],hors:28,host:[3,7,9,15,17,18,20,23,27,29,31,33,35,36,37,41,44],hostnam:[3,20],hour:45,hours_on_queu:45,how:[7,15,20,29,30,33,37,38,39,42,44],howev:[0,16],http:[3,16,20,28,33,42],human:[0,30,42,45],i:[2,7,8,28],id:[0,2,4,5,6,7,13,15,16,18,21,22,23,24,25,26,28,29,30,31,33,34,35,36,37,38,40,41,42,43,44,45],ident:30,identifi:[26,30,42],idx_max:44,idxmax:44,ie:3,ignor:[21,22,34],illustr:[33,37,44],iloc:44,imag:[2,5,12,28,30],image2:[17,18],image_dataset:17,image_fil:17,image_filename_col:[5,17,28],img:33,implicitli:32,importantli:16,includ:[4,6,7,8,13,16,20,28,39,42,43,45],inclus:8,increas:8,index:[17,30],indic:[8,34],indico:[0,1,2,3,4,5,6,7,8,9,10,11,13,14,15,16,17,18,21,22,23,24,25,26,27,28,29,30,31,32,33,34,35,36,37,38,39,40,41,42,43,44,45],indico_api_token:[3,9,15,17,18,20,23,27,29,31,33,35,36,37,41,44],indico_api_token_path:[3,20],indico_host:[3,20],indicocli:[3,7,9,15,17,18,19,20,23,27,29,31,33,35,36,37,41,44],indicoconfig:[1,9,15,17,18,19,23,27,29,31,33,35,36,37,41,44],indicoerror:5,indicoinputerror:34,indicoio:23,indicorequesterror:[1,13],indicotimeouterror:[21,34],individu:[24,38,42],info:38,inform:[6,7,13,16,38,39,42],inherit:32,initi:30,inlcud:0,inlin:8,input:[8,14,42],input_filenam:[14,30,42],input_imag:[26,28],input_ocr_extract:[26,41],inputfil:11,instanc:2,instanti:20,instead:[3,23,28],integ:[30,42],integr:42,intend:[7,8],interact:[1,20],intern:32,invalid:3,invoic:42,io:[3,9,15,16,17,18,20,29,31,32,33,35,36,37,41,42,44],ipa:[1,8,16],isinst:33,ital:8,item:[0,28,33,45],iter:37,its:[28,30,41,42],jame:30,job:[6,7,13,16,18,19,23,26,27,28,31,33,34,35,37,38,41,42],job_id:[37,38],job_opt:23,jobid:16,jobstatu:[6,7,16,18,21,23,27,28,29,31,33,35,37,38,41],john:30,jpg:17,json:[1,6,7,8,16,20,21,28,30,32,37,39,42],json_config:[6,7,16,29,31],json_result:[23,29],jsonconfig:16,jsonstr:[16,26,34],just:[2,27,37,42],jwt:20,keep:[2,27],kei:[0,3,8,19,23,28,32],key_class:41,know:[8,23,30,37],kwarg:[3,4,8,11,22,24,25,38,42,45],label:[0,13,24,28,30,41,45],label_typ:8,labeled_sampl:23,labelresolutionstrategi:13,labelset:[4,13,16,26,41],labelset_by_nam:[23,28,35,41],labelset_column_id:[26,28,41],labelset_id:[13,23,28,35,41],labelset_nam:41,larg:[20,32],later:32,latest:[24,27],latter:8,learn:[20,24],left:[8,27,28],legaci:[6,7,8],len:[0,37],length:42,let:30,level:[6,7,12,39,45],librari:[2,3,16,20],libreari:20,like:[0,8,16,17,20,22,26,28,30,42],limit:[5,9,10,13,16,33,34,37,39,40],line:[8,23],link:[41,42],linkedlabelgroup:41,linkedlabelstrategi:41,list:[0,4,5,6,7,8,9,13,15,16,18,23,26,27,28,29,30,32,33,34,38,40,41,42,43,44,45],listdataset:[2,5,16],listsubmiss:[30,33,34],listworkflow:[40,41,42,44],live:28,ll:[20,27],load:[16,26,27,28,44],local:[12,28,32],locat:[4,8,20,28],log:[37,38],longer:[23,37],look:[3,16,20,28,29,30,42],loop:42,looser:8,lot:[7,8],lr:28,machin:24,made:[28,30,38],mai:[29,41],make:[1,2,16,20,22,34],manag:30,mani:[6,7,16,21,22,23,38,39],manual:[0,20,30],map:[38,42],mark:[4,30,33,34,42],match:23,max:5,max_it:28,maximum:[20,34],mean:[28,30,42],messag:16,metadata:[4,6,7,16,23],metadatalist:16,metric:[2,7,8,12,19],mg:[23,36],might:[20,30],migrat:19,mimic:[6,8],minut:45,moddat:8,model:[0,6,7,8,12,13,16,19,29,30,33,35,41,42,45],model_group:[24,26,35,41],model_group_by_nam:[35,41],model_group_id:[36,41,45],model_id:[13,18,23,26,27,28,35],model_predict_arg:16,model_training_opt:[26,28],model_typ:26,modelgroup:[15,16,23,24,26],modelgroupid:16,modelgrouppredict:[16,18,22,23,26,28,35],modelgroupreq:41,modelid:16,modelpredict:16,modelstpmetr:45,modeltasktyp:41,modifi:0,more:[2,6,7,8,16,20,23,24,27,35,42],most:[2,7,8,16,20,32,34,44],move:20,much:23,multipl:[2,13,27,42],must:[0,16,28,30,34],mutat:16,my:[15,16,17,23,27,28,30],my_classification_model:[23,35],my_compani:20,my_config:[9,15,17,20,23,27,29,31,33,35,36,37,41,44],my_dataset:16,my_fil:[0,33],my_ocr_config:7,my_url:33,myco:3,mycompani:[20,23,27],myfil:28,myfile2:28,myother:16,n:33,name:[0,4,5,14,15,16,17,23,24,26,28,30,35,36,38,39,41,42,45],nativ:[6,7],native_pdf:8,navig:2,need:[0,7,8,26,27,32],nest:[6,7],new_labelset:41,new_labelset_arg:[26,41],new_questionnaire_arg:26,new_workflow:[28,41],newdataset:16,newlabelsetargu:[26,41],newquestionnaireargu:26,next:28,none:[1,5,6,10,13,14,21,26,30,32,34,39,40,44],normal:0,not_enough_data:35,notabl:32,note:[0,3,6,16,21,29,30,42],notic:30,notif:42,now:[9,23,28,37,41,44],num_pag:4,num_pr:45,number:[4,5,16,27,34,39,42,45],nummodelgroup:15,nymber:45,object:[1,3,5,6,7,8,13,16,19,20,22,24,26,29,30,32,34,37,40,42],occur:8,ocr:[6,8,12,16,19,30,41,42],ocr_engin:5,off:[27,34],often:[1,20,21,32],old:[2,23],older:[6,23],omnipage_ocr_opt:5,onc:[27,30],ondocu:[6,7,8,16,31],one:[6,7,8,16,17,27,30,34,41,42,43],onli:[0,7,8,26,27,28,32,37,41,43,44],open:28,oper:[5,8,22,23,27,32,42],optic:6,option:[1,3,5,7,8,13,14,16,20,21,23,26,30,34,40,43,44,45],or_:[33,37],order:[34,42],order_bi:34,orderbi:34,organ:42,origin:[7,8],other:[0,29,33,34],out:34,output:[7,8,42],over:[20,37],own:20,ox:28,oxford:28,page:[0,2,4,6,7,9,10,12,16,18,23,27,30,36,39,42],page_foot:8,page_head:8,page_id:4,page_index:8,page_num:8,page_offset:8,page_s:34,pagerot:8,pagg:4,pagin:[9,33,34,37],panda:[13,17,44],paragraph:29,paramet:[1,3,5,6,13,14,21,26,28,32,34,39,40,41,43],parameter:16,parent:26,pars:12,part:25,particular:[2,38],pass:[7,8,20,23,27,28,30,42,43],path:[3,7,9,15,16,17,18,20,23,27,28,29,30,31,33,35,36,37,41,42,44],path_to_doc:[7,31,33],path_to_docu:7,path_to_fil:23,pathnam:[5,6,16],pd:[17,44],pdf:[0,2,6,7,16,23,29,30,31,33,41,42],pdf_extract:[6,7,8,23],pdfversion:8,pending_admin_review:[14,30],pending_auto_review:[30,34],pending_review:[14,30],per:[13,39,41,42,45],percent:[25,36,45],percent_complet:[25,36],perform:[0,2,6,8,24],period:34,permiss:[4,16,38],persist:[30,42],piec:29,pip:20,pixel:8,place:[16,20,30,34],platform:[1,2,3,4,7,20,21,22,24,25,27,28,32,36,42],platfrom:28,pleas:[0,6],png:[17,18,28,33],poll:5,posit:[6,7],possibl:[8,30],power:20,pre:0,pre_review:30,preced:26,pred:[0,33],pred_label:0,predcit:16,predicion:30,predict:[0,2,6,12,13,16,19,26,30,34,42,45],predict_opt:26,predictionmetr:45,predictopt:16,prefix:8,present:[0,28,45],preset:6,preset_config:[6,7,8,16,29,31],previou:26,previous_dataset:38,previous_rol:38,previously_en:38,primari:1,primarlili:4,princip:[7,8],print:[15,18,20,27,30,31,33,36,37,42,44],prior:[2,8,23,26,38,42],probabl:[7,8],problem:[8,16],process:[1,4,8,14,28,30,32,33,34,41,42,43,45],produc:8,programat:[0,30],programmat:0,progress:[12,25],proper:20,properli:16,provid:[1,6,7,8,16,18,28,30,34],publicli:17,pull:[37,45],push:42,python:[7,8,16,20],ql:37,qstr:15,queri:[0,5,6,7,10,12,13,14,17,18,19,21,23,26,27,28,29,30,31,32,33,34,35,36,37,39,40,41,42,43,44],query_arg:16,questionnair:26,queu:[22,45],queue:[0,34,43,45],queuemetr:45,quit:32,r:28,rainbow_url:4,rais:[1,3,5,6,13,21,26,34],ran:[7,8],rang:[8,9],rather:8,raw:[6,7,34],raw_result:[0,33],raw_text:23,re:23,read:[8,20],read_api_ocr_opt:5,readi:[16,18,22,30],reason:2,receiev:42,receiv:8,recent:34,recognit:6,recommend:[16,34],record:8,refer:[20,28],reivew:[30,45],reject:[22,30,33,34,44,45],rejected_in_review:[44,45],relat:16,reliabl:8,remain:2,remov:5,removedatasetfil:5,replac:[16,23,41],report:[12,19,37,38,39],report_format:39,repres:[24,28,42],request:[1,3,7,10,32,34,38,39,41,43,45],request_interv:21,requestchain:1,requests_param:3,requir:[8,16,18,20,23,30,33,34],resolut:8,respons:[1,6,7,8,10,15,28,45],result:[0,4,6,7,9,12,16,18,21,23,27,28,30,31,32,33,34,35,37,41,42],result_fil:[0,30,33],result_url:[30,33],result_vers:40,retain:8,retrain:[2,24],retri:[22,34],retriev:[0,4,5,14,30,32,33,34,35,42,44],retrievestorageobject:[0,6,7,23,29,30,31,32,33,37,41,42],retrysubmiss:34,review:[2,14,19,24,27,33,34,36,42,43,45],review_denom:45,review_id:30,review_not:30,review_numer:45,review_reject:30,review_stp_pct:45,reviewen:34,reviewer_id:30,revok:22,right:[0,8,28],robot:28,role:[37,38,39],row:[2,4,8,13],row_count:4,row_end:8,row_start:8,rowcount:[15,16],run:[12,27],runtimeerror:[1,3],s:[2,3,4,6,7,8,16,18,20,23,24,25,27,30,37,38,41,42,44],said:38,sampl:[7,8,10,12,18,23,26,27,30,35,41,42],sample1:30,sandbox:20,save:2,scan:[6,7,8],schema:16,script:[0,18,19,30],second:[7,8,21,34],section:[20,42],see:[2,5,6,10,16,23,27,28,30,42],select:[7,18,23,24,26,28,37,44],selected_model:35,selectedmodel:16,send:[0,1,12,15,30,41],sent:42,separ:8,serv:8,session:3,set:[0,3,6,7,16,19,20,23,37,42],sever:[2,42],shell:20,ship:20,shorter:0,should:[0,3,8,17,20,23,26,28,32,42],show:[15,17,25,27,29,44],shown:[0,7,8],similar:[7,8],simpl:[6,7,8,12,20,41],simpli:8,sinc:8,singl:[7,8,12,13,42],single_column:[8,23],size:[4,5,6,7],slightli:[18,29],smaller:29,smith:30,snapshot:37,snippet:[17,30,42],so:[27,37],softwar:28,solv:24,some:[2,16,32],someth:26,soon:33,sophist:7,sourc:[16,26,28,30],source_column_id:[23,26,28,35,41],span:8,specif:[0,8,30,39,42,43,44,45],specifi:[0,8,17,45],spend:45,spent:45,split:29,spreadsheet:8,src_path:6,ssl:3,standard:[6,7,8,23,29,42],start:[19,30,37,39,43],start_dat:[37,39,43,44],state:[30,34],statu:[4,5,14,15,16,19,22,24,25,26,30,31,33,34,35,36,42],status:[30,42],status_meta:4,step:[0,8,26,41,42],still:[0,16],storag:[13,19,28,30,37],storage_object:32,storageobject:21,store:[4,17,32],stp:[44,45],stpmetric:45,str:[3,4,5,6,14,16,22,24,25,26,32,34,37,38,39,44,45],straight:[43,45],straight_through_process:[43,44,45],straightthroughprocess:45,strategi:[8,41],strategy_set:41,stream:[32,40],string:[7,14,16,26,32],strongli:16,structur:8,sub_filt:33,submiss:[0,12,14,19,30,40,41,42,43,44,45],submission_id:[0,30,33,34,41],submissionfilt:[14,30,33,34],submissionmetr:45,submissionresult:[30,33,34,41,42],submit:[0,30,33,34,42,44,45],submitreview:[0,33,34],subs_on_queu:45,success:[5,16,22,31],suit:7,summar:39,summari:[37,38,39],suppli:45,support:[8,34],sure:[3,16,23],system:42,t:[8,16,28,30],tab:42,tabl:23,table_read_ord:8,tabular:8,take:30,talk:28,target:35,target_1:35,target_class:23,target_nam:41,task:[2,24,26,45],task_typ:[24,41],tasktyp:16,teach:[2,24],terminolog:[19,23],test:[16,41],test_paragraph:29,test_siz:28,text:[0,3,5,6,7,16,18,23,29,30,35],text_by_block:29,text_by_pag:29,text_color:8,than:[0,8,23,27,29,34],thei:[8,16,18,28,30],them:[8,27,28,32,37],therefor:16,thi:[0,4,6,7,8,14,21,23,25,26,27,28,30,34,37,38,41,42,44,45],thing:[2,20,33],think:[2,24],those:[8,30,34,42],thousand:[2,27],three:[28,41,42],through:[0,9,12,30,42,43,45],throughout:8,tif:[2,6,7],tight:8,time:[24,34,38,45],time_on_task:45,timedelta:37,timeontaskmetr:45,timeout:[21,34],titl:8,to_csv:17,to_datetim:44,todai:[37,43],togeth:42,token:[3,6,7,20],token_index:8,tool:28,top:[2,8,28],top_level:8,total:[43,45],total_sub:44,track:42,train:[2,6,7,8,12,24,25,26,27,29,42],training_mg:36,training_progress:[25,36],trainingprogress:25,treat:27,tutori:20,two:[17,41,42],txt:[3,9,15,17,18,20,23,27,29,31,33,35,36,37,41,44],type:[5,9,19,21,26,32,34,35,37,40,41,42,44],typic:[26,34],ui:[2,41],uk:28,unabl:16,under:28,underlin:8,unifi:42,uniqu:[7,30,42],univers:28,unknown:42,unnest:[6,8],until:34,up:42,updat:[26,34,41],updated_bi:38,updated_workflow:[35,41],updater_email:38,updatesubmiss:[30,33,34],upgrad:20,upload:[5,6,16,18,32],upload_batch_s:6,uploaddocu:[28,32],uploadimag:18,upper:[8,27],url:[4,13,17,18,20,21,28,30,32,33,40,42],url_prefix:28,us:[3,4,6,7,8,16,17,18,20,21,23,26,28,29,30,32,33,37,38,41,42,44],usag:0,use_small_model:28,user:[0,3,7,8,12,13,16,20,30,34,40,45],user_email:38,user_id:[37,38],user_metr:[37,38],user_summari:37,userchangelog:[37,38],userchangelogreport:38,userdataset:38,userid:37,usermetr:[37,39],usermetricsfilt:[37,39],usersnapshot:38,usersnapshotfilt:39,usersummari:[37,38],usersummarycount:38,usual:24,util:8,v3:23,valid:[3,8,42],valu:[8,28,45],vanilla:8,vari:29,variabl:[3,7,16,42],varieti:[7,8],vdp:8,ve:[8,28,30],verbos:20,veri:42,verifi:[3,20],verify_ssl:3,version:[2,23,27],vgg:28,via:[0,22,28],view:30,visibl:[34,40],visit:27,vs:23,w:16,wa:[4,6,28,30,34,38,44],wai:[1,17,20],wait:[5,6,7,13,16,18,21,23,26,27,28,29,30,31,33,34,35,37,41,42,45],waitforsubmiss:[0,33,34],want:[16,20,27,28,29,37,41,42],watch:34,we:[7,8,16,27,28,41,42],web:20,well:[8,16],were:[0,7,8,38],wf_result:41,what:[17,28,30,42],when:[0,2,14,16,22,28,30,42],whenev:42,where:[2,7,8,17,42],whether:[8,17,28,30,42],which:[8,26,28,30,37,38,42],who:[7,8],whole:8,whose:38,width:8,wish:0,within:[0,2,4,8,28,34,42],without:[8,33,42],won:8,work:[6,7,8,16,18,42],workflow:[0,12,16,19,26,28,30,34,35],workflow_id:[0,26,28,30,33,34,40,41,42,43,44,45],workflow_metr:[43,44,45],workflow_nam:[28,41],workflowmetr:[44,45],workflowmetricsopt:[43,44,45],workflowopt:43,workflowstpmetr:45,workflowsubmiss:[0,14,30,33,40,41,42],workflowsubmissiondetail:33,worklow:44,would:[0,8,16,20,23,26],wow:37,www:28,x:[8,44],y:8,yield:34,you:[0,2,7,8,16,17,18,20,22,23,24,27,28,29,30,32,34,37,41,42],your:[0,2,3,5,6,7,15,16,17,18,20,23,30,35,41,42,44]},titles:["Auto Review","IndicoClient","Key Concepts and Terminology","IndicoConfig","Dataset Types","Datasets","DocumentExtraction","OCR With DocumentExtraction","DocumentExtraction Settings","Query for Document Report","Document Report","Document Report Types","Examples","Exports","Filters","Simple GraphQL Query Example","Common GraphQL Queries","Created a Dataset from Local Images","Get Predictions from Image Model","indicoio Python Client Library","Getting Started","Jobs and Job Status","Jobs Types","Migrating Client Library Scripts","Model Group Types","Model Types","Model Groups","Generating Model Predictions","Object Detection","Parsing the OCR result at the document, page, and block levels","Review","OCR a Single File with DocumentExtraction","Storage","Sending New Samples to a Workflow (aka Workflow Submission)","Submissions","Train a Classifier and Predict","Check Model Training Progress","Fetching User Metrics","User Metrics Types","User Metrics","Workflows","Run Files Through a Workflow","Workflows","Workflow Metrics","Fetching Workflow Metrics","Workflow Metrics Types"],titleterms:{"class":20,"export":13,"import":27,"new":33,No:0,With:7,accept:0,aka:33,altern:8,api:[20,30,42],authent:[20,23],auto:0,block:[8,29],built:20,call:27,charact:[8,23],check:36,classifi:35,client:[19,20,23],common:16,concept:2,confid:8,configur:[7,8,20],creat:17,dataset:[2,4,5,17,28],detail:8,detect:28,document:[0,8,9,10,11,29],documentextract:[6,7,8,31],dot:8,dpi:8,environ:20,exampl:[12,15],fetch:[37,44],file:[31,41],filter:14,find:27,forc:8,from:[17,18],gener:27,get:[18,20,23],global:8,granular:8,graphql:[15,16,20],group:[2,24,26],guid:19,id:27,imag:[8,17,18],inch:8,indico:20,indicocli:1,indicoconfig:[3,20],indicoio:19,inform:8,initi:23,instal:20,introduct:[0,7,28,30,42],job:[21,22],kei:2,label:2,level:[8,29],librari:[19,23],local:17,metadata:8,metric:[37,38,39,43,44,45],migrat:23,model:[2,18,23,24,25,26,27,28,36],modelgrouppredict:27,nativ:8,nest:8,note:27,number:8,object:28,ocr:[7,23,29,31],offset:8,optic:23,order:8,other:8,page:[8,29],pars:[8,29],pdf:8,per:8,perform:27,posit:8,pre:20,predict:[18,23,27,28,35],preset:[7,8],progress:36,python:19,queri:[9,15,16,20],reblock:8,recognit:23,refer:19,reject:0,render:8,report:[9,10,11],result:[8,29],review:[0,30],run:[41,42],sampl:33,schema:20,script:23,select:[2,27],send:33,set:[2,8],simpl:15,singl:31,size:8,start:20,statu:21,storag:32,style:8,submiss:[33,34],tabl:8,terminolog:2,text:8,through:41,thumbnail:8,token:8,train:[23,28,35,36],type:[4,8,11,22,24,25,38,45],upload:28,us:0,user:[19,37,38,39],valu:0,variabl:20,via:[30,42],workflow:[33,40,41,42,43,44,45],your:[27,28]}})