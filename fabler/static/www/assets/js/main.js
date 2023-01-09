// 'use strict';

var Fabler = Fabler || {};


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


let main = (() => {
  document.querySelector("form").onsubmit = (event) => {
    event.preventDefault();
    let prompt_text = document.getElementById("prompt_text").value;
    let num_sentences = document.getElementById("num_sentences").value;
    fetch(`/?prompt_text=${encodeURIComponent(prompt_text)}&num_sentences=${encodeURIComponent(num_sentences)}`)
      .then( response => response.json() )
      .then( response => {
        console.log(response);
        console.log(response.generation);
        // response.generation.forEach((res) => {
        //   console.log(res);
        //   answers = parse_response(query_text, res['generated_text']);
        //   output_element.value = `${answers}\n${output_element.value}`;
        // });
      });

  };
})();


void 0;
