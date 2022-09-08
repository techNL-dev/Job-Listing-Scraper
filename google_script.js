function doGet() {
  // Get the spreadsheet
  let sh1 = SpreadsheetApp.getActiveSpreadsheet().getSheetByName("Sheet1");
  // Fetch the endpoint
  let res = UrlFetchApp.fetch(
    "https://data.mongodb-api.com/app/sheetsconnection-qhmpk/endpoint/GetCollection"
  );
  // Convert the response to an array of objects
  let mongoArray = Array.from(JSON.parse(res.getContentText()));
  // If the array is empty do nothing
  if (mongoArray.length === 0) {
    return;
  }
  // Otherwise clear the spreadsheet
  sh1.clear();
  // Append the keys to the top
  let keys = Object.keys(mongoArray[0]);
  sh1.appendRow(keys);
  // Append the data
  for (let i = 0; i < mongoArray.length; i++) {
    let vals = Object.values(mongoArray[i]);
    sh1.appendRow(vals);
  }
  let range = sh1.getRange("A1");
  sh1.hideColumn(range);
}

function onEdit(e) {
  let sh1 = SpreadsheetApp.getActiveSpreadsheet().getSheetByName("Sheet1");
  let changedCell = e.source.getCurrentCell();
  let changedRowIndex = changedCell.getRowIndex();
  if (changedRowIndex === 1) {
    return;
  }

  console.log("Changed Row Index:");
  console.log(changedRowIndex);

  let idCell = sh1.getRange("A" + changedRowIndex);
  let id = idCell.getValue();

  let keyRow = sh1.getRange("1:1");
  let keys = keyRow.getValues()[0].filter((item) => item !== "");
  let keyCount = keys.length;
  console.log("Keys:");
  console.log(keys);
  console.log("Range: (" + changedRowIndex + ":" + changedRowIndex + ")");
  let valRow = sh1.getRange("" + changedRowIndex + ":" + changedRowIndex);
  let vals = valRow.getValues()[0].filter((_item, index) => index < keyCount);
  console.log("Values:");
  console.log(vals);

  let newDoc = {};
  for (let i = 1; i < keyCount; i++) {
    newDoc[keys[i]] = vals[i];
  }

  console.log("New Doc");
  console.log(newDoc);

  let payload = {
    id: id,
    update: { $set: newDoc },
  };

  var params = {
    method: "post",
    payload: JSON.stringify(payload),
  };
  UrlFetchApp.fetch(
    "https://data.mongodb-api.com/app/sheetsconnection-qhmpk/endpoint/UpdateDoc",
    params
  );
}
