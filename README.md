# Setup 
```
docker-compose up --build 
```

# Debugging common issues 
If the database is not automatically migrated, you may need to run 
```
docker-compose down --volumes
```

# Access frontend on http://localhost:3000