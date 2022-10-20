const SerpApi = require('google-search-results-nodejs');
const search = new SerpApi.GoogleSearch("77d42f93e427e34b242e026ca50ec287a1ba19f514ce6f7540fea89866845001");

const params = {
  engine: "google_scholar_author",
  hl: "en",
  author_id: "abU3flQAAAAJ"
};

const callback = function(data) {
  console.log(data);
};

// Show result as JSON
search.json(params, callback);