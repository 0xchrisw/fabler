// 'use strict';


let parse_response = (query_text, response) => {
  let responses = response.split(query_text).at(-1);

  responses = response.split("\n").map((res) => {
    if(res.toLowerCase().startsWith("query:")) {
      return res.slice(6).trim();
    }
  });
  responses = responses.filter((res) => { return res });

  return responses.join("---\n");
};


document.querySelector("form").onsubmit = (event) => {
  event.preventDefault();
  let selection = document.querySelector("select").selectedIndex;
  console.log(selection);
};


(() => {
  window.addEventListener("load", () => {
    let query_element = document.getElementById("query_text");
    let output_element = document.getElementById("output");

    // query_element.value = "";
    output_element.value = "";

    query_element.addEventListener("keyup", (event) => {
      let query_text = event.target.value.trim();

      if(query_text.length > 4) {
        console.log(`Key pressed: ${event.key}`);
        console.log(`Query text: ${query_text}`);
        let query_params = `query: ${encodeURIComponent(query_text)}`;

          fetch(`http://127.0.0.1:9000/?text=${query_params}`)
            .then( response => response.json() )
            .then( response => {
              console.log(response);
              console.log(response.generation);
              response.generation.forEach((res) => {
                console.log(res);
                answers = parse_response(query_text, res['generated_text']);
                output_element.value = `${answers}\n${output_element.value}`;
              });
            });
      }
    });
  });
})();

void 0;
