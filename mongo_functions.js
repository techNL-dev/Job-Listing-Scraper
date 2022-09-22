// GetCollectionCurrent
exports = function () {
  const allDocs = context.services
    .get("mongodb-atlas")
    .db("JobListingScraper")
    .collection("Listing")
    .find();

  console.log(allDocs);

  return allDocs;
};

// GetCollectionPrevious
exports = function () {
  const allDocs = context.services
    .get("mongodb-atlas")
    .db("JobListingScraper")
    .collection("PreviousListing")
    .find();

  console.log(allDocs);

  return allDocs;
};

// UpdateDocCurrent
exports = function (request, response) {
  // Get the body of the request
  const body = JSON.parse(request.body.text());
  console.log(JSON.stringify(body));
  //Get the objects id
  let id = body.id;
  console.log(`ID: ${id}`);
  // Get the collection
  var collection = context.services
    .get("mongodb-atlas")
    .db("JobListingScraper")
    .collection("Listing");
  // Get the object
  collection.findOne({ _id: BSON.ObjectId(id) }).then((doc) => {
    console.log(JSON.stringify(doc));
  });
  // Update the object
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

// UpdateDocPrevious
exports = function (request, response) {
  // Get the body of the request
  const body = JSON.parse(request.body.text());
  console.log(JSON.stringify(body));
  //Get the objects id
  let id = body.id;
  console.log(`ID: ${id}`);
  // Get the collection
  var collection = context.services
    .get("mongodb-atlas")
    .db("JobListingScraper")
    .collection("PreviousListing");
  // Get the object
  collection.findOne({ _id: BSON.ObjectId(id) }).then((doc) => {
    console.log(JSON.stringify(doc));
  });
  // Update the object
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
