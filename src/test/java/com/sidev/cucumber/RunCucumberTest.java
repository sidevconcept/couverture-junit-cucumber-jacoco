package com.sidev.cucumber;

import io.quarkiverse.cucumber.CucumberQuarkusTest;

/**
 * Point d'entree Cucumber pour Quarkus : cette classe est decouverte par Surefire
 * (mvn test) comme n'importe quel test JUnit, et delegue a Cucumber la decouverte
 * des fichiers .feature et des classes de step definitions du module.
 */
public class RunCucumberTest extends CucumberQuarkusTest {
}
