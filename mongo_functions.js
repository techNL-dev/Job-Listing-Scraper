// GetCollection
exports = function () {
  const allDocs = context.services
    .get("mongodb-atlas")
    .db("SheetsDB")
    .collection("SheetsCollection")
    .find();

  console.log(allDocs);

  return allDocs;
};

// UpdateDoc
exports = function (request, response) {
  const body = JSON.parse(request.body.text());
  console.log(JSON.stringify(body));
  let id = body.id;
  console.log(`ID: ${id}`);
  /*Accessing application's values:
  var x = context.values.get("value_name");*/

  //Accessing a mongodb service:
  var collection = context.services
    .get("mongodb-atlas")
    .db("SheetsDB")
    .collection("SheetsCollection");
  collection.findOne({ _id: BSON.ObjectId(id) }).then((doc) => {
    // do something with doc
    console.log(JSON.stringify(doc));
  });
  collection.updateOne(
    { _id: BSON.ObjectId(id) },
    body.update,
    function (err, res) {
      if (err) throw err;
      console.log("1 document updated");
    }
  );
  return;
};
