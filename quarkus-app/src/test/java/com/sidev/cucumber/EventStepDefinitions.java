package com.sidev.cucumber;

import io.cucumber.java.en.Given;
import io.cucumber.java.en.Then;
import io.cucumber.java.en.When;
import io.restassured.response.Response;

import static io.restassured.RestAssured.given;
import static org.hamcrest.MatcherAssert.assertThat;
import static org.hamcrest.Matchers.equalTo;
import static org.hamcrest.Matchers.notNullValue;
import static org.hamcrest.Matchers.hasSize;

/**
 * Etapes Cucumber pour les scenarios de src/test/resources/features/gestion_evenements.feature.
 * Les appels passent par l'API REST (RestAssured), exactement comme le ferait un vrai client :
 * ce sont des tests de comportement de bout en bout, distincts des tests unitaires JUnit.
 */
public class EventStepDefinitions {

    private Response lastResponse;

    @Given("mon agenda est vide pour le {string}")
    public void mon_agenda_est_vide_pour_le(String date) {
        // Rien a faire : chaque scenario utilise une date dediee, donc l'agenda
        // est de fait vide pour cette date au demarrage du scenario.
    }

    @Given("j'ai déjà l'événement {string} de {string} à {string} le {string}")
    public void jai_deja_levenement(String titre, String debut, String fin, String date) {
        creerEvenement(titre, debut, fin, date);
    }

    @When("je crée l'événement {string} de {string} à {string} le {string}")
    public void je_cree_levenement(String titre, String debut, String fin, String date) {
        creerEvenement(titre, debut, fin, date);
    }

    @When("je consulte ma journée du {string}")
    public void je_consulte_ma_journee_du(String date) {
        lastResponse = given()
                .queryParam("date", date)
                .when().get("/api/calendrier/evenements");
    }

    @Then("l'événement {string} apparait dans ma journée du {string}")
    public void levenement_apparait_dans_ma_journee(String titre, String date) {
        given()
                .queryParam("date", date)
                .when().get("/api/calendrier/evenements")
                .then()
                .statusCode(200)
                .body("events.title", hasSize(1))
                .body("events[0].title", equalTo(titre));
    }

    @Then("la création est refusée pour cause de conflit d'horaire")
    public void la_creation_est_refusee_pour_conflit() {
        assertThat(lastResponse.statusCode(), equalTo(409));
    }

    @Then("le message de jour férié est présent dans la réponse")
    public void le_message_de_jour_ferie_est_present() {
        lastResponse.then().body("holidayGreeting", notNullValue());
    }

    private void creerEvenement(String titre, String debut, String fin, String date) {
        String body = """
                {
                  "title": "%s",
                  "start": "%sT%s:00",
                  "end": "%sT%s:00",
                  "category": "TRAVAIL"
                }
                """.formatted(titre, date, debut, date, fin);

        lastResponse = given()
                .contentType("application/json")
                .body(body)
                .when().post("/api/calendrier/evenements");
    }
}
