/*
 * JPMS strict (Vidocq oblige) : requires explicites, exports minimaux.
 * Coordonnees et structure verifiees contre l'exemple officiel
 * vidocq-runtime-cassini-rest-example (tag v0.3.0) — voir PROMPT.md.
 */
module com.sidev.vidocqapp {
    requires jakarta.cdi;
    requires jakarta.inject;
    requires jakarta.ws.rs;
    requires jakarta.json.bind;

    requires io.vidocq.runtime.core;
    requires io.vidocq.runtime.spi;
    requires io.vidocq.runtime.extensions.jakartaee.core.cassini;
    requires io.vidocq.cassini.api;
    requires io.vidocq.chappe.api;
    requires io.vidocq.vauban.core;

    // Zero opens/exports sur resource et service : la decouverte des beans CDI
    // (Vauban) et des ressources REST (Cassini) passe par les fichiers
    // META-INF/services generes par les annotation processors, pas par la
    // reflexion classique. Seuls les DTO serialises en JSON-B ont besoin
    // d'etre exportes (publicLookup de Yasson).
    exports com.sidev.agenda.model;
    exports com.sidev.agenda.resource.dto;

    // io.vidocq.runtime.core.Vidocq instancie AgendaApp par reflexion
    // (Constructor.newInstance) au demarrage — sans cet export, echec avec
    // IllegalAccessException des le lancement de l'image jlink.
    exports com.sidev.vidocqapp;

    // Sans le layer applicatif Vauban (voir plus bas), le conteneur CDI a besoin
    // d'un acces reflexif normal (opens) sur les packages contenant les beans -
    // sinon Vauban.BeanManager ne les voit tout simplement jamais et
    // VaubanBeanProvider#getResourceClasses() renvoie un ensemble vide (d'ou
    // les 404 silencieux, sans la moindre exception).
    opens com.sidev.agenda.resource;
    opens com.sidev.agenda.service;

    // La decouverte automatique (promotion des META-INF/services generes en
    // "provides" synthetiques) n'existe que pour le lancement @VidocqMain via
    // le layer applicatif Vauban (voir la javadoc de Vidocq.run). En lancement
    // "runtime-first" (java -m io.vidocq.runtime.core/...Vidocq, celui utilise
    // par l'image jlink), notre module est un vrai module nomme du module-graph
    // de boot : le ServiceLoader ignore alors les META-INF/services et exige un
    // "provides" explicite. D'ou cette declaration, a la main, pour chaque
    // ressource REST generee par cassini-processor.
    provides io.vidocq.cassini.spi.gen.ResourceAdapter
            with com.sidev.agenda.resource.CalendarResource$$CassiniAdapter;
    provides io.vidocq.cassini.spi.gen.RouteProvider
            with com.sidev.agenda.resource.CalendarResource$$CassiniRoutes;
}
