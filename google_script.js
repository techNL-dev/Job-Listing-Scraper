// Some constant data
const DATA = {
  current: {
    sheetName: "Current",
    // The URL to the GetCollectionCurrent endpoint
    getCollectionURL: ScriptProperties.getProperty("GetCurrent"),
    // The URL to the UpdateCollectionCurrent endpoint
    updateDocURL: ScriptProperties.getProperty("UpdateCurrent"),
  },
  previous: {
    sheetName: "Previous",
    // The URL to the GetCollectionPrevious endpoint
    getCollectionURL: ScriptProperties.getProperty("GetPrevious"),
    // The URL to the UpdateCollectionPrevious endpoint
    updateDocURL: ScriptProperties.getProperty("UpdatePrevious"),
  },
};

function doGet(e) {
  // Set up the "state"
  const previous = e !== undefined && e.parameter.current === "previous";
  const state = DATA[previous ? "previous" : "current"];
  console.log(`Get ${state["sheetName"]}`);
  // Get the spreadsheet
  let sh1 = SpreadsheetApp.getActiveSpreadsheet().getSheetByName(
    state["sheetName"]
  );

  // Fetch the endpoint
  let res = UrlFetchApp.fetch(state["getCollectionURL"]);
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

  // Hide the columns with the object ids and descriptions
  let range = sh1.getRange("A1");
  sh1.hideColumn(range);
  range = sh1.getRange("D1");
  sh1.hideColumn(range);
  range = sh1.getRange("E1");
  sh1.hideColumn(range);
}

function edit(e) {
  // Set up the "state"
  const previous = e.source.getActiveSheet().getName() !== "Current";
  const state = DATA[previous ? "previous" : "current"];
  console.log(`Edit ${state["sheetName"]}`);

  // Get the spreadsheet
  let sh1 = SpreadsheetApp.getActiveSpreadsheet().getSheetByName(
    state["sheetName"]
  );
  // Get the cell of that changed
  let changedCell = e.source.getCurrentCell();
  let changedRowIndex = changedCell.getRowIndex();
  if (changedRowIndex === 1) {
    return;
  }
  // Get the id of the object that had the value changed
  let idCell = sh1.getRange("A" + changedRowIndex);
  let id = idCell.getValue();

  // Get the keys (headings)
  let keyRow = sh1.getRange("1:1");
  let keys = keyRow.getValues()[0].filter((item) => item !== "");
  let keyCount = keys.length;
  console.log("Keys:");
  console.log(keys);
  // Get the values of the row where the cell was edited
  let valRow = sh1.getRange("" + changedRowIndex + ":" + changedRowIndex);
  let vals = valRow.getValues()[0].filter((_item, index) => index < keyCount);
  console.log("Values:");
  console.log(vals);

  // Set up the payload so that the edit will be applied on the MongoDB side
  let newDoc = {};
  let changedColIndex = e.source.getCurrentCell().getColumnIndex() - 1;
  newDoc[keys[changedColIndex]] = vals[changedColIndex];
  let payload = {
    id: id,
    update: { $set: newDoc },
  };

  // Set up the request parameters
  let params = {
    method: "post",
    payload: JSON.stringify(payload),
  };
  // Make the request to the updateDocURL
  UrlFetchApp.fetch(state["updateDocURL"], params);
}
