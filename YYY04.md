# ***Математическая модель Промышленного кластера*** 
[!IMPORTANT]
Директива актуальности: всякий раз, когда пользователь сообщает о загрузке новой или исправленной модели (например, "Работаем с новой моделью", "Загрузил модель с исправлениями"), считай, что это полностью самостоятельный и независимый документ. Ты должен забыть все детали и выводы из любых предыдущих версий модели. Все твои ответы должны строиться на основе строгого анализа данных только из текущего, последнего предоставленного файла.

[!IMPORTANT]
Все ответы должны строиться только на основе загруженной модели.
Если запрос требует конкретных значений - просто выдавай SQL-запрос, без выдуманных данных.
SQL должен быть совместим с SQL Server версии  до 2017.
Выдавать результат в нормализованном виде, пригодном для дальнейшей SQL-обработки, не используй текстовую агрегацию.
Считай аргументами для поиска (where) только уникальные значения, если в запросе нет прямого указания на поиск по имени.
Всегда указывай какое множество из модели отражает запрос.   
Нельзя делать выводы "по интуиции" или "по смыслу". Если в данных есть противоречивость:  сообщи об этом и останови дальнейшее выполнение задания.  
Если нет подходящих данных в DB, используй  запросы к AP. 

### Сокращения 
ПК - Промышленный кластер,
УК  - Участник ПК,
ЯПК - Ядро ПК,
НП  - номенклатура продукции  кластера = продукция кластера,
ППК - Продукт ПК,
ВПК - Внешний потребитель ППК,
СППК - Система планирования ПК,
DB - База данных,
AS - Сервер приложений
$\mathbb{R}^+$  - положительные действительные числа.

### Правила 
Проверка аксиомы - это  запрос к DB, возращающий: 0 - аксиома не выполняется, 1 - аксиома выполняется

## $S$ - формальная математическая модель ПК 

$S=\langle C,\overline{C},P,R,\overline{R}, \overline{\overline{R}}\rangle$ \- система ПК, где

$C=\{c_1, ..., c_n\}$ - перечень УК,

$\overline{C}\subset C$ - ЯПК

$P=\{p_1, ..., p_n\}$ -  перечень НП (типы товаров/услуг, которые могут производиться в кластере),


$R\subseteq C \times P$ - перечень ППК,
ППК - это  $\langle c_i,p_j,\rangle$ где  $\langle c_i,p_j,\rangle \in R$  -  это пары <УК,НП>,
h = $\left| R \right|$  - количество продуктов.

$
 \overline{R}\subset R
$   - подмножество продуктов, производимых для  ВПK,  
$\overline{h} = \left|\overline{R} \right|$  - количество продуктов, производимых для  ВПK.   


$ A = \{a_{i,j} \} $ - матрица затрат размерности $h \times h,  a_{i,j} \in \{0\} \cup  \mathbb{R}^+$, где
$a_{i,j}$ - это количество  ППК(ресурса)  $ r_i \in R$,  необходимого для изготовления 1(единицы) ППК (изделия) $r_j \in R$.

$\overline{\overline{R}} \subset R \times R
$   - звенья технологических цепей, $\overline{\overline{R}}  \equiv \{ \langle  r_i, r_j \rangle | a_{i,j} > 0 \}$,
$ r_i $ - ППК, который являются ресурсом для изготовления  $ r_j $,
$ r_j $ - ППК, который  изготавливается из ресурсов  $ r_i $ .
- Аксимы для $S$
1) $ \forall(i=\overline{1,h}) 0 \leq a_{i,i} < 1 $


## Формальные определения понятий 
$ r_i \in R $ - конечный ППК, если   $ \nexists( r_j\neq r_i) |\langle r_i, r_j \rangle \in \overline{\overline{R}} $.  

$ r\in R $ - ППК только для внутреннего  потербления, eсли 
  $ r \not\in \overline{R} $.

 $r\in R $ - ППК промежуточный, eсли    $ r \not\in \overline{R} \land
  \exist (r_i\neq r,r_j\neq r)| \{\langle r_i, r \rangle , \langle r, r_j \rangle \} \subset \overline{\overline{R}} $

## $H_S$ -  СППК  $S$ 

$ H_S = \langle A, Y, \tau \rangle$ - СППК для кластера $S$, где     
$Y = (y_1,  y_2, ...,y_h )^T $   - вектор-столбец размености $h = \left|  Y \right|$,  $y_i \geq 0$ -  объем (колличество) ППК  $r_i$, запланированного для ВПК,  
 $\tau$ - период планирования (например: год, полугодие, квартал, месяц, неделя, дни, ..).        

$ \pi =\langle X, Y \rangle$  - план в  $ H_S$, где   
 $X = (x_1,  x_2, ...,x_h )^T $ - вектор-столбец, размерности $h = \left|  X \right|$ -  решение системы линейных уравнений    $X-AX=Y$, $X$ - валоавый план произволства продуктов $r_i, i=$,  $x_i$ - валовой план производства продукта $r_i$. 

- Аксиомы для $H_S$  
 2) $ \forall(r_i \in R- \overline{R}): y_i =0 $  
 3) $ \exist(r_i \in  \overline{R})| y_i > 0 $
 4) $ \det(A) \neq 0  $

##  DB: ПК  
-    $P=\{p_1, ..., p_n\}$   
CREATE TABLE Production   -- НП  
(  
	ID   varchar(10) NOT NULL,   -- идентификатор НП  
	NAME nchar(50) NOT NULL,     -- наименование  НП  
    CONSTRAINT [PK_Production] PRIMARY KEY CLUSTERED (ID ASC)  
)  
-  $C=\{c_1, ..., c_n\}$    
CREATE TABLE ClusterMember    --  УК   
(  
    ID     varchar(10) NOT NULL, -- идентификатор УК  
 	NAME   nchar(50) NOT NULL,   -- наименование  УК  
	ISCORE bit       NOT NULL,   -- принадлежит ЯПК?  $\overline{C}\subset C$ - ЯПК    
	CONSTRAINT [PK_ClusterMember] PRIMARY KEY CLUSTERED (ID ASC)  
)  
 - $R\subseteq C \times P$   
CREATE TABLE Product    -- ППК     
(  
	ID                 varchar(20) NOT NULL,   -- идентификатор  ППК
	ID_PRODUCTION      varchar(10) NOT NULL,   -- идентификатор  НП
	ID_CLUSTERMEMBER   varchar(10) NOT NULL,   -- идентификатор  УК   
  NAME               nchar(50)   NOT NULL, 
	ISEXT              bit         NOT NULL,   -- для ВПК?    $ \overline{R}\subset R$ 
	CONSTRAINT [PK_Product]      PRIMARY KEY CLUSTERED (ID ASC),   
	CONSTRAINT FK_Prodiction     FOREIGN KEY (ID_PRODUCTION) REFERENCES Production (ID),    
	CONSTRAINT FK_ClusterMember  FOREIGN KEY (ID_CLUSTERMEMBER) REFERENCES СlusterMember(ID)      
) 

 - $ A = \{a_{i,j} \}$,   $\overline{\overline{R}} \subset R \times R$
 - в таблице Cost хранятся только значения  $a_{i,j} > 0$,
 - если в таблице  Cost нет значения, то  $a_{i,j} = 0$
CREATE TABLE Cost
(
	ID_PRODUCT_RESOURCE     varchar(20) NOT NULL,   -- $i, r_i$
	ID_PRODUCT_RESULT       varchar(20) NOT NULL,   -- $j, r_j $
	COEFFICIENT             decimal (18,8) NOT NULL, -- $ a_{i,j}>0$
  CONSTRAINT [PK_Cost]      PRIMARY KEY CLUSTERED   (ID_PRODUCT_RESOURCE, ID_PRODUCT_RESULT  ASC),
	CONSTRAINT FK_Product_Resource      FOREIGN KEY (ID_PRODUCT_RESOURCE) REFERENCES Product (ID),
	CONSTRAINT FK_Product_Result        FOREIGN KEY (ID_PRODUCT_RESULT)   REFERENCES  Product (ID)
)
- $Y = (y_1,  y_2, ...,y_h )^T $  
- таблица  ExtConsumerPlan идентификатор плана, период и комментарии к плану    
- в таблице  PlanValue  хранятся только значения  $y_i > 0$,  
CREATE TABLE ExtConsumerPlan  
(
	ID                  varchar(10) NOT NULL,   - $\tau$ - период планирования   
	PERIOD              int         NOT NULL,   --   $\tau$ - период планирования   
	COMMENT             nchar(200)   -- комментарии к плану
	CONSTRAINT [PK_ExtConsumerPlan]   PRIMARY KEY CLUSTERED (ID  ASC)
)
CREATE TABLE PlanValue    -- $Y = (y_1,  y_2, ...,y_h )^T$
(
	ID_PRODUCT          varchar(20) NOT NULL,  -- $ r_i$  
	VALUE               decimal (18,8) NOT NULL check (VALUE >= 0),  -- $y_i$   
	ID_EXTCONSUMERPLAN  varchar(10) NOT NULL,   -- ID плана    
 	CONSTRAINT [PK_PlanValue]   PRIMARY KEY CLUSTERED (ID_PRODUCT ASC),   
	CONSTRAINT [FK_ExtConsumerPlan]     FOREIGN KEY (ID_EXTCONSUMERPLAN) REFERENCES ExtConsumerPlan (ID) ON  DELETE CASCADE,   
	CONSTRAINT [FK_Product]     FOREIGN KEY (ID_PRODUCT) REFERENCES Product (ID) ON  DELETE CASCADE   
) 




##  AP: ПК. запросы

### вычислить $ \det(A)$
- формат запроса
{
  "jsonrpc": "2.0",
  "method": "calcdet",
  "params":  
  \{  
    $\hspace{5mm}$"H": $h$,  //  h = $\left| R \right|$  - количество продуктов  
   $\hspace{5mm}$ "A":    // по строкам матрицы $A$, только ненулевые элементы 
   $\hspace{10mm}$\{  
   $\hspace{10mm}$    "ID_RESOURCE_1": \{ "ID_RESULT_1a":  $a_{id\_resource_1, id\_result_1a}$,  ..., "ID_RESULT_1z": $a_{id\_resource_1, id\_result_1z}$    \},  
   $\hspace{10mm}$ ...,      
   $\hspace{10mm}$ "ID_RESOURCE_M": \{ "ID_RESULT_Ma":  $a_{id\_resource_M, id\_result_Ma}$,..., "ID_RESULT_Mz": $a_{id\_resource_M, id\_result_Mz}$  \}  
  $\hspace{10mm}$ \} // $ A = \{a_{i,j} \} $   
  \},
  "id": 1
}
- формат ответа
{
  "jsonrpc": "2.0",
  "result":  $ \det(A)$,
  "id": 1
}


### вычислить план   $X = (x_1,  x_2, ...,x_h )^T $  
- формат запроса   
{   
  "jsonrpc": "2.0",   
  "method": "calcplan ",      
  "params":  
  \{  
    $\hspace{5mm}$  "H": $h$,  //  h = $\left| R \right|$  - количество продуктов  
    $\hspace{5mm}$  "Y":  // столбец Y  
     $\hspace{10mm}$ \{  
     $\hspace{10mm}$   "ID_PRODUCT_1": $y_{id\_product_1}$ ,..., "ID_PRODUCT_N":$y_{id\_product_N}$   
     $\hspace{10mm}$  \}  ,   //  $Y = (y_1,  y_2, ...,y_h )$  
   $\hspace{5mm}$ "A":    // по строкам матрицы $A$, только ненулевые элементы   
   $\hspace{10mm}$\{  
   $\hspace{10mm}$    "ID_RESOURCE_1": \{ "ID_RESULT_1a":  $a_{id\_resource_1, id\_result_1a}$,  ..., "ID_RESULT_1z": $a_{id\_resource_1, id\_result_1z}$    \},  
   $\hspace{10mm}$ ...,      
   $\hspace{10mm}$ "ID_RESOURCE_M": \{ "ID_RESULT_Ma":  $a_{id\_resource_M, id\_result_Ma}$,..., "ID_RESULT_Mz": $a_{id\_resource_M, id\_result_Mz}$  \}  
  $\hspace{10mm}$ \} // $ A = \{a_{i,j} \} $   
  \},
  "id": 1
}
- формат ответа
{
  "jsonrpc": "2.0",
  "result":
   \{
    $\hspace{5mm}$  "X":  // столбец X
    $\hspace{10mm}$ \{
     $\hspace{10mm}$   "ID_PRODUCT_1": $x_{id\_product_1}$ ,..., "ID_PRODUCT_N":$x_{id\_product_N}$
     $\hspace{10mm}$  \}  ,   //  $X = (x_1,  x_2, ...,x_h )$  
   \}
  "id": 1
}
