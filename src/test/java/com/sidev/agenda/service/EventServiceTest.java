package com.sidev.agenda.service;

import com.sidev.agenda.model.Event;
import com.sidev.agenda.model.EventCategory;
import io.quarkus.test.junit.QuarkusTest;
import jakarta.inject.Inject;
import org.junit.jupiter.api.Test;

import java.time.LocalDateTime;
import java.util.List;

import static org.junit.jupiter.api.Assertions.assertEquals;
import static org.junit.jupiter.api.Assertions.assertThrows;

@QuarkusTest
class EventServiceTest {

    @Inject
    EventService eventService;

    @Test
    void creeUnEvenementEtLeRetrouveParDate() {
        LocalDateTime start = LocalDateTime.of(2026, 10, 1, 9, 0);
        LocalDateTime end = LocalDateTime.of(2026, 10, 1, 10, 0);

        eventService.create(new Event(null, "Revue de sprint", start, end, EventCategory.TRAVAIL));

        List<Event> events = eventService.findByDate(start.toLocalDate());
        assertEquals(1, events.size());
        assertEquals("Revue de sprint", events.get(0).title());
    }

    @Test
    void refuseUnEvenementQuiChevaucheUnEvenementExistant() {
        LocalDateTime start = LocalDateTime.of(2026, 10, 2, 9, 0);
        LocalDateTime end = LocalDateTime.of(2026, 10, 2, 10, 0);
        eventService.create(new Event(null, "Point client", start, end, EventCategory.TRAVAIL));

        Event chevauchant = new Event(null, "Autre reunion", start.plusMinutes(30), end.plusMinutes(30), EventCategory.TRAVAIL);

        assertThrows(EventConflictException.class, () -> eventService.create(chevauchant));
    }
}
