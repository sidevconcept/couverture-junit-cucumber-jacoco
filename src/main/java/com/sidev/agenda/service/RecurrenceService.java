package com.sidev.agenda.service;

import com.sidev.agenda.model.Event;
import jakarta.enterprise.context.ApplicationScoped;

import java.util.ArrayList;
import java.util.List;

/**
 * Genere les occurrences d'un evenement recurrent a partir d'un evenement modele.
 * NB : la frequence MENSUELLE s'appuie sur LocalDateTime#plusMonths, qui "ecrete"
 * automatiquement les jours qui n'existent pas dans le mois suivant (ex: 31 janvier
 * -> 28 ou 29 fevrier). C'est volontairement la branche la moins testee du projet :
 * lors de la conference, c'est elle qu'on montrera comme "classe a mieux couvrir".
 */
@ApplicationScoped
public class RecurrenceService {

    public List<Event> generate(Event template, RecurrenceFrequency frequency, int occurrences) {
        if (occurrences < 1) {
            throw new IllegalArgumentException("Le nombre d'occurrences doit etre au moins 1");
        }

        List<Event> generated = new ArrayList<>();
        for (int i = 0; i < occurrences; i++) {
            generated.add(shift(template, frequency, i));
        }
        return generated;
    }

    private Event shift(Event template, RecurrenceFrequency frequency, int step) {
        return switch (frequency) {
            case QUOTIDIENNE -> new Event(
                    null,
                    template.title(),
                    template.start().plusDays(step),
                    template.end().plusDays(step),
                    template.category());
            case HEBDOMADAIRE -> new Event(
                    null,
                    template.title(),
                    template.start().plusWeeks(step),
                    template.end().plusWeeks(step),
                    template.category());
            case MENSUELLE -> new Event(
                    null,
                    template.title(),
                    template.start().plusMonths(step),
                    template.end().plusMonths(step),
                    template.category());
        };
    }
}
