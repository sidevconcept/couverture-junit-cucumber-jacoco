package com.sidev.agenda.service;

import jakarta.enterprise.context.ApplicationScoped;

import java.time.LocalDate;
import java.util.List;

/**
 * Bonus "sympa" de l'agenda : une citation du jour sur les tests et la qualite du code.
 * Sans test unitaire dedie, elle n'est couverte que par ricochet via le endpoint
 * GET /api/calendrier/evenements -> bon exemple de couverture "accidentelle",
 * a nuancer en conference : couverte au sens Jacoco ne veut pas dire testee expres.
 */
@ApplicationScoped
public class QuoteOfTheDayService {

    private static final List<String> CITATIONS = List.of(
            "Le code sans tests, c'est une legende urbaine : tout le monde en parle, personne ne l'a verifie.",
            "Un rapport de couverture a 100% ne garantit rien ; a 0%, il garantit le pire.",
            "Ecrire un test, c'est ecrire une question a laquelle le code doit repondre.",
            "La couverture de code mesure ce qui a ete execute, pas ce qui a ete verifie.",
            "Le meilleur moment pour ecrire un test etait avant le bug. Le deuxieme, c'est maintenant.");

    public String quoteOfTheDay(LocalDate date) {
        int index = date.getDayOfYear() % CITATIONS.size();
        return CITATIONS.get(index);
    }
}
