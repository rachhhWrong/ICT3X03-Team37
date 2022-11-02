db.createUser(
    {
        user: process.env.MONGO_NONROOT_USERNAME,
        pwd: process.env.MONGO_NONROOT_PASSWORD,
        roles: [{ role: "readWrite", db: process.env.MONGO_INITDB_DATABASE}]
    }
)