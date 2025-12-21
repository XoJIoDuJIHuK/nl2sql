
use IndustrialCluster;




-- ClusterMemeber
--ID	NAME	ISCORE
--C1	C1                                                	1
--C2	C2                                                	1
--C3	C3                                                	1
--C4	C4                                                	0
--C5	C5                                                	0
--C6	C6                                                	0
--C7	C7                                                	0


--ID	ID_PRODUCTION	ID_CLUSTERMEMBER	NAME	ISEXT
--C1/PCA	PCA	C1	C1/PCA                                            	1
--C1/PCB	PCB	C1	C1/PCB                                            	1
--C2/PCA	PCA	C2	C2/PCA                                            	1
--C2/PCB	PCB	C2	C2/PCB                                            	1
--C3/MB	    MB	C3	C3/MB                                             	0
--C3/SUA	SUA	C3	C3/SUA                                            	1
--C4/CPS	CPS	C4	C4/CPS                                            	1
--C5/RAM	RAM	C5	C5/RAM                                            	1
--C6/MG	MG	C6	    C6/MG                                             	0
--C7/WAR	WAR	C7	C7/WAR                                            	0



use IndustrialCluster
go

insert ExtConsumerPlan(id,  period, comment) values ('0000000001',  1, 'test');
--
insert PlanValue(id_product,  value, id_extconsumerplan) values ('C1/PCA', 10000, '0000000001');
insert PlanValue(id_product,  value, id_extconsumerplan) values ('C1/PCB', 15000, '0000000001');
insert PlanValue(id_product,  value, id_extconsumerplan) values ('C2/PCA', 20000, '0000000001');
insert PlanValue(id_product,  value, id_extconsumerplan) values ('C2/PCB', 10000, '0000000001');
insert PlanValue(id_product,  value, id_extconsumerplan) values ('C3/SUA',  5000, '0000000001');
insert PlanValue(id_product,  value, id_extconsumerplan) values ('C3/MB',   1000, '0000000001');
insert PlanValue(id_product,  value, id_extconsumerplan) values ('C4/CPS',  2000, '0000000001');
insert PlanValue(id_product,  value, id_extconsumerplan) values ('C5/RAM', 10000, '0000000001');
insert PlanValue(id_product,  value, id_extconsumerplan) values ('C6/MG',   5000, '0000000001');




 delete Cost;
 insert Cost(id_product_resource, id_product_result, coefficient) values ('C3/SUA', 'C2/PCA',  1);
 insert Cost(id_product_resource, id_product_result, coefficient) values ('C3/MB',  'C1/PCA',  1);
 insert Cost(id_product_resource, id_product_result, coefficient) values ('C3/MB',  'C1/PCB',  1);
 insert Cost(id_product_resource, id_product_result, coefficient) values ('C3/MB',  'C2/PCB',  1);
 insert Cost(id_product_resource, id_product_result, coefficient) values ('C3/MB',  'C3/SUA',  1);
 insert Cost(id_product_resource, id_product_result, coefficient) values ('C3/MB',  'C7/WAR',  0.001);

 insert Cost(id_product_resource, id_product_result, coefficient) values ('C4/CPS',  'C1/PCA',  1);
 insert Cost(id_product_resource, id_product_result, coefficient) values ('C4/CPS',  'C1/PCB',  1);
 insert Cost(id_product_resource, id_product_result, coefficient) values ('C4/CPS',  'C2/PCB',  1);
 insert Cost(id_product_resource, id_product_result, coefficient) values ('C4/CPS',  'C3/SUA',  1);
 insert Cost(id_product_resource, id_product_result, coefficient) values ('C4/CPS',  'C7/WAR',  0.01);
 insert Cost(id_product_resource, id_product_result, coefficient) values ('C5/RAM',  'C1/PCA',  2);
 insert Cost(id_product_resource, id_product_result, coefficient) values ('C5/RAM',  'C1/PCB',  4);
 insert Cost(id_product_resource, id_product_result, coefficient) values ('C5/RAM',  'C2/PCB',  4);
 insert Cost(id_product_resource, id_product_result, coefficient) values ('C5/RAM',  'C3/SUA',  2);
 insert Cost(id_product_resource, id_product_result, coefficient) values ('C5/RAM',  'C7/WAR',  0.001);


 insert Cost(id_product_resource, id_product_result, coefficient) values ('C6/MG',  'C1/PCA',  1);
 insert Cost(id_product_resource, id_product_result, coefficient) values ('C6/MG',  'C1/PCB',  1);
 insert Cost(id_product_resource, id_product_result, coefficient) values ('C6/MG',  'C2/PCA',  1);
 insert Cost(id_product_resource, id_product_result, coefficient) values ('C6/MG',  'C2/PCB',  1);
 insert Cost(id_product_resource, id_product_result, coefficient) values ('C6/MG',  'C7/WAR',  0.005);

 insert Cost(id_product_resource, id_product_result, coefficient) values ('C7/WAR',  'C1/PCA',  1);
 insert Cost(id_product_resource, id_product_result, coefficient) values ('C7/WAR',  'C1/PCB',  1);
 insert Cost(id_product_resource, id_product_result, coefficient) values ('C7/WAR',  'C2/PCA',  1);
 insert Cost(id_product_resource, id_product_result, coefficient) values ('C7/WAR',  'C2/PCB',  1);

    

 
    





--go     
        
        


