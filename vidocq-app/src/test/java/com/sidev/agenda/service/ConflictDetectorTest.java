package com.sidev.agenda.service;

import com.sidev.agenda.model.Event;
import com.sidev.agenda.model.EventCategory;
import org.junit.jupiter.api.Test;

import java.time.LocalDateTime;
import java.util.UUID;

import static org.junit.jupiter.api.Assertions.assertFalse;
import static org.junit.jupiter.api.Assertions.assertTrue;

class ConflictDetectorTest {

    private final ConflictDetector detector = new ConflictDetector();

    private Event eventAt(String id, int startHour, int endHour) {
        LocalDateTime day = LocalDateTime.of(2026, 9, 9, 0, 0);
        return new Event(
                id == null ? null : UUID.nameUUIDFromBytes(id.getBytes()),
                "evenement",
                day.withHour(startHour),
                day.withHour(endHour),
                EventCategory.TRAVAIL);
    }

    @Test
    void deuxEvenementsQuiSeChevauchentSontEnConflit() {
        Event a = eventAt("a", 9, 11);
        Event b = eventAt("b", 10, 12);

        assertTrue(detector.isConflicting(a, b));
        assertTrue(detector.isConflicting(b, a));
    }

    @Test
    void deuxEvenementsQuiSeTouchentNeSontPasEnConflit() {
        Event a = eventAt("a", 9, 10);
        Event b = eventAt("b", 10, 11);

        assertFalse(detector.isConflicting(a, b));
    }

    @Test
    void deuxEvenementsSepareSNeSontPasEnConflit() {
        Event a = eventAt("a", 9, 10);
        Event b = eventAt("b", 14, 15);

        assertFalse(detector.isConflicting(a, b));
    }

    @Test
    void unEvenementNEstJamaisEnConflitAvecLuiMeme() {
        Event a = eventAt("a", 9, 11);

        assertFalse(detector.isConflicting(a, a));
    }
}
