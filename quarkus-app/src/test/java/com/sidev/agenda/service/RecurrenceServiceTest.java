package com.sidev.agenda.service;

import com.sidev.agenda.model.Event;
import com.sidev.agenda.model.EventCategory;
import org.junit.jupiter.api.Test;

import java.time.LocalDateTime;
import java.util.List;

import static org.junit.jupiter.api.Assertions.assertEquals;
import static org.junit.jupiter.api.Assertions.assertThrows;

/**
 * Volontairement incomplet : seules les frequences QUOTIDIENNE et HEBDOMADAIRE sont
 * testees ici. La branche MENSUELLE (voir RecurrenceService) n'a aucun test alors
 * qu'elle contient le cas limite le plus interessant (fin de mois / annee bissextile).
 * C'est l'exemple choisi pour la conference pour montrer une couverture "partielle".
 */
class RecurrenceServiceTest {

    private final RecurrenceService recurrenceService = new RecurrenceService();

    @Test
    void genereLeBonNombreDOccurrencesQuotidiennes() {
        List<Event> occurrences = recurrenceService.generate(dailyStandup(), RecurrenceFrequency.QUOTIDIENNE, 5);

        assertEquals(5, occurrences.size());
        assertEquals(LocalDateTime.of(2026, 9, 11, 9, 0), occurrences.get(4).start());
    }

    @Test
    void genereDesOccurrencesHebdomadaires() {
        List<Event> occurrences = recurrenceService.generate(dailyStandup(), RecurrenceFrequency.HEBDOMADAIRE, 3);

        assertEquals(3, occurrences.size());
        assertEquals(LocalDateTime.of(2026, 9, 21, 9, 0), occurrences.get(2).start());
    }

    @Test
    void refuseUnNombreDOccurrencesInvalide() {
        assertThrows(IllegalArgumentException.class,
                () -> recurrenceService.generate(dailyStandup(), RecurrenceFrequency.QUOTIDIENNE, 0));
    }

    private Event dailyStandup() {
        LocalDateTime start = LocalDateTime.of(2026, 9, 7, 9, 0);
        LocalDateTime end = LocalDateTime.of(2026, 9, 7, 9, 15);
        return new Event(null, "Daily standup", start, end, EventCategory.TRAVAIL);
    }
}
