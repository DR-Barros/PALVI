# Decisiones tecnicas:
- para simular un backend real se genero un backend con FASTAPI bien minimalista, que me retorne los datos que necesito para datasets y fecha especifica
- se creo un endpoint que utiliza llm para generar insights positivos y negativos, a partir de un dataset y fecha especifica de forma dinamica, lo que me permite obtener los datos mas relevantes para cada fecha y dataset.
- Se subdividio la pagina en 4 secciones, cada una con su propio componente, lo que me permite tener un codigo mas organizado y facil de mantener.
- por temas de tiempo, gran parte del desarrollo se realizo con los agentes de github copilot, para maximizar la velocidad de desarrollo.
- En general el desarrollo consto de la primera hora de chatear con chatgpt para definir que KPIs son los que necesitaria un jefe de ventas para tomar decisiones, y luego se desarrollo el backend y frontend de forma simultanea, para ir probando los endpoints a medida que se iban creando, lo que me permitio tener un feedback constante sobre el funcionamiento del sistema.
- Para facilitar la visualizacion de los datos, la vista consiste en un resumen ejecutivo generado por ia y luego 3 secciones de kpis para navegar entre ellas

# Siguiente Iteracion:
- Incorporar autenticación y manejo de usuarios para personalizar dashboards según el perfil del cliente.
- Reemplazar datasets simulados por integración con fuentes de datos reales o pipelines ETL.
- validar LLM con expertos en ventas para asegurar que los insights generados sean relevantes y accionables.
- Mejorar la interfaz de usuario con gráficos interactivos y visualizaciones avanzadas para facilitar la interpretación de los datos.
- Implementar un sistema de alertas o notificaciones para informar a los usuarios sobre cambios significativos en los KPIs o insights generados por la IA.
- Pulir el codigo, si bien intente modularizarlo lo mas posible, el tiempo me jugo en contra y se que hay partes del codigo que se pueden mejorar, tanto en el backend como en el frontend.


# Ejecución:
- Para ejecutar el proyecto, primero se debe clonar el repositorio y luego seguir instrucciones en los readme de cada carpeta.