FROM maven:3.9-eclipse-temurin-17 AS builder
WORKDIR /build

# Copiar pom.xml
COPY pom.xml .

# Descargar dependencias
RUN mvn dependency:go-offline

# Copiar código fuente (la ruta es src, no java-spring/src)
COPY src ./src

# Compilar
RUN mvn clean package -DskipTests

# Imagen final
FROM eclipse-temurin:17-jdk-alpine
WORKDIR /app

# Copiar el JAR desde el builder
COPY --from=builder /build/target/*.jar app.jar

EXPOSE 8086

ENTRYPOINT ["java", "-jar", "/app/app.jar"]