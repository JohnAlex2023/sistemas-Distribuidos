from pyspark import SparkConf, SparkContext

# Configuramos Spark y creamos el contexto
conf = SparkConf().setAppName("WordCount").setMaster("local[*]")
sc = SparkContext(conf=conf)

# Cargamos el archivo de texto
lines = sc.textFile("ruta/al/archivo.txt")

# Dividimos cada línea en palabras
words = lines.flatMap(lambda line: line.split())

# Convertimos cada palabra en minúscula y la asignamos a una tupla (palabra, 1)
word_tuples = words.map(lambda word: (word.lower(), 1))

# Sumamos los valores por cada palabra para obtener el conteo
word_counts = word_tuples.reduceByKey(lambda a, b: a + b)

# Mostramos los resultados
for word, count in word_counts.collect():
    print(f"{word} : {count}")

# Cerramos el contexto de Spark
sc.stop()
