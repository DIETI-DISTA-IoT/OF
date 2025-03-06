window.addEventListener('DOMContentLoaded', (event) => {

  const produceAllButton = document.getElementById("produce-all");
  const consumeAllButton = document.getElementById("consume-all");
  const stopProduceAllButton = document.getElementById("stop-producing-all");
  const stopConsumeAllButton = document.getElementById("stop-consuming-all");
  const startWandbButton = document.getElementById("start-wandb");
  const stopWandbButton = document.getElementById("stop-wandb");
  const createVehiclesButton = document.getElementById("create-vehicles");
  const deleteVehiclesButton = document.getElementById("delete-vehicles");
  const startFederatedLearningButton = document.getElementById("start-federated-learning");
  const stopFederatedLearningButton = document.getElementById("stop-federated-learning");
  const startAttack = document.getElementById("start-attack");
  const stopAttack = document.getElementById("stop-attack");


  produceAllButton.addEventListener("click", function() {
      fetch("/produce-all", {method: "POST"})
        .then(response => response.text())
        .then(data => console.log(data));
  });

  consumeAllButton.addEventListener("click", function() {
      fetch("/consume-all", {method: "POST"})
        .then(response => response.text())
        .then(data => console.log(data));
  });

  stopProduceAllButton.addEventListener("click", function() {
      fetch("/stop-producing-all", {method: "POST"})
        .then(response => response.text())
        .then(data => console.log(data));
  });

  stopConsumeAllButton.addEventListener("click", function() {
      fetch("/stop-consuming-all", {method: "POST"})
        .then(response => response.text())
        .then(data => console.log(data));
  });

  startWandbButton.addEventListener("click", function() {
      fetch("/start-wandb", {method: "POST"})
        .then(response => response.text())
        .then(data => console.log(data));
  });

  stopWandbButton.addEventListener("click", function() {
      fetch("/stop-wandb", {method: "POST"})
        .then(response => response.text())
        .then(data => console.log(data));
  });

  startAttack.addEventListener("click", function() {
    fetch("/start-attack", {method: "POST"})
      .then(response => response.text())
      .then(data => console.log(data));
  });

  createVehiclesButton.addEventListener("click", function() {
      fetch("/create-vehicles", {method: "POST"})
        .then(response => response.text())
        .then(data => console.log(data));
  });

  deleteVehiclesButton.addEventListener("click", function() {
      fetch("/delete-vehicles", {method: "POST"})
        .then(response => response.text())
        .then(data => console.log(data));
  });

  startFederatedLearningButton.addEventListener("click", function() {
      fetch("/start-federated-learning", {method: "POST"})
        .then(response => response.text())
        .then(data => console.log(data));
  });

  stopFederatedLearningButton.addEventListener("click", function() {
      fetch("/stop-federated-learning", {method: "POST"})
        .then(response => response.text())
        .then(data => console.log(data));
  });
});