package com.sidev.vidocqapp;

import io.vidocq.runtime.core.Vidocq;
import io.vidocq.runtime.spi.VidocqApp;
import io.vidocq.runtime.spi.VidocqMain;

/**
 * Point d'entree de l'agenda malin sur Vidocq. API REST {@code /api/calendrier/evenements}
 * fournie par Cassini, servie par Chappe, CDI par Vauban — meme domaine que
 * com.sidev.agenda du module quarkus-app.
 * <p>
 * {@code main} ne doit contenir QUE {@code Vidocq.run(...)} : le runtime
 * re-resout l'application dans un layer de module enfant (weaving des client
 * proxies) avant d'executer {@link #run}. Toute logique ecrite avant
 * {@code Vidocq.run(...)} s'executerait dans le mauvais classloader, contre des
 * classes non transformees.
 */
@VidocqMain
public class AgendaApp implements VidocqApp {

    static void main(String[] args) {
        Vidocq.run(AgendaApp.class, args);
    }

    @Override
    public int run(String... args) throws Exception {
        Vidocq.waitForExit();
        return 0;
    }
}
