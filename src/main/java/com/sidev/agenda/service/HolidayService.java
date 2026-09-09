package com.sidev.agenda.service;

import jakarta.enterprise.context.ApplicationScoped;

import java.time.LocalDate;
import java.time.MonthDay;
import java.util.Map;

/**
 * Petit service "sympa" : signale les jours feries fixes francais.
 * Volontairement sans test unitaire dedie : seule la methode greetingFor() est
 * exercee indirectement via le scenario Cucumber "jour ferie". isHoliday() n'est
 * jamais appelee directement par un test -> bon exemple, dans le rapport Jacoco,
 * d'une couverture "de passage" a completer par un vrai test unitaire.
 */
@ApplicationScoped
public class HolidayService {

    private static final Map<MonthDay, String> JOURS_FERIES = Map.of(
            MonthDay.of(1, 1), "Jour de l'an",
            MonthDay.of(5, 1), "Fete du travail",
            MonthDay.of(5, 8), "Victoire 1945",
            MonthDay.of(7, 14), "Fete nationale",
            MonthDay.of(8, 15), "Assomption",
            MonthDay.of(11, 1), "Toussaint",
            MonthDay.of(11, 11), "Armistice 1918",
            MonthDay.of(12, 25), "Noel");

    public boolean isHoliday(LocalDate date) {
        return JOURS_FERIES.containsKey(MonthDay.from(date));
    }

    public String greetingFor(LocalDate date) {
        String label = JOURS_FERIES.get(MonthDay.from(date));
        if (label == null) {
            return null;
        }
        return "🎉 " + label + " : profitez-en pour ne rien planifier !";
    }
}
