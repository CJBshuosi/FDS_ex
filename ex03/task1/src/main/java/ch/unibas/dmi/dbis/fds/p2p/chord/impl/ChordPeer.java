package ch.unibas.dmi.dbis.fds.p2p.chord.impl;

import ch.unibas.dmi.dbis.fds.p2p.chord.api.*;
import ch.unibas.dmi.dbis.fds.p2p.chord.api.ChordNetwork;
import ch.unibas.dmi.dbis.fds.p2p.chord.api.data.Identifier;
import ch.unibas.dmi.dbis.fds.p2p.chord.api.data.IdentifierCircle;
import ch.unibas.dmi.dbis.fds.p2p.chord.api.data.IdentifierCircularInterval;
import ch.unibas.dmi.dbis.fds.p2p.chord.api.math.CircularInterval;

import java.util.Random;
import java.util.Map;
import java.util.concurrent.ConcurrentHashMap;

import static ch.unibas.dmi.dbis.fds.p2p.chord.api.data.IdentifierCircularInterval.createOpen;
import static ch.unibas.dmi.dbis.fds.p2p.chord.api.data.IdentifierCircularInterval.createRightOpen;
import static ch.unibas.dmi.dbis.fds.p2p.chord.api.data.IdentifierCircularInterval.createLeftOpen;
/**
 * TODO: write JavaDoc
 *
 * @author loris.sauter
 */
public class ChordPeer extends AbstractChordPeer {
  /**
   *
   * @param identifier
   * @param network
   */
  protected ChordPeer(Identifier identifier, ChordNetwork network) {
    super(identifier, network);
  }

  /**
   * Asks this {@link ChordNode} to find {@code id}'s successor {@link ChordNode}.
   *
   * Defined in [1], Figure 4
   *
   * @param caller The calling {@link ChordNode}. Used for simulation - not part of the actual chord definition.
   * @param id The {@link Identifier} for which to lookup the successor. Does not need to be the ID of an actual {@link ChordNode}!
   * @return The successor of the node {@code id} from this {@link ChordNode}'s point of view
   */
  @Override
  public ChordNode findSuccessor(ChordNode caller, Identifier id) {
    /* TODO: Implementation required. */
    ChordNode nprime = this.findPredecessor(caller, id);
    return nprime.successor(); // First element in the finger table is the successor
  }

  /**
   * Asks this {@link ChordNode} to find {@code id}'s predecessor {@link ChordNode}
   *
   * Defined in [1], Figure 4
   *
   * @param caller The calling {@link ChordNode}. Used for simulation - not part of the actual chord definition.
   * @param id The {@link Identifier} for which to lookup the predecessor. Does not need to be the ID of an actual {@link ChordNode}!
   * @return The predecessor of or the node {@code of} from this {@link ChordNode}'s point of view
   */
  @Override
  public ChordNode findPredecessor(ChordNode caller, Identifier id) {
    /* TODO: Implementation required. */
    ChordNode nprime = this;

    IdentifierCircularInterval interval = createLeftOpen(nprime.id(), nprime.successor().id());
    while (!interval.contains(id)) {
      nprime = nprime.closestPrecedingFinger(caller, id);
      interval = createLeftOpen(nprime.id(), nprime.successor().id());
    }
    return nprime;
  }

  /**
   * Return the closest finger preceding the  {@code id}
   *
   * Defined in [1], Figure 4
   *
   * @param caller The calling {@link ChordNode}. Used for simulation - not part of the actual chord definition.
   * @param id The {@link Identifier} for which the closest preceding finger is looked up.
   * @return The closest preceding finger of the node {@code of} from this node's point of view
   */
  @Override
  public ChordNode closestPrecedingFinger(ChordNode caller, Identifier id) {
    /* TODO: Implementation required. */
    for (int i = getNetwork().getNbits(); i >= 1; i--) {
      if (this.fingerTable.node(i).isPresent()) {
        ChordNode finger_i = this.fingerTable.node(i).get();
        if (createOpen(this.id(), id).contains(finger_i.id())) {
          return finger_i;
        }
      }
    }
    return this;
  }

  /**
   * Called on this {@link ChordNode} if it wishes to join the {@link ChordNetwork}. {@code nprime} references another {@link ChordNode}
   * that is already member of the {@link ChordNetwork}.
   *
   * Required for static {@link ChordNetwork} mode. Since no stabilization takes place in this mode, the joining node must make all
   * the necessary setup.
   *
   * Defined in [1], Figure 6
   *
   * @param nprime Arbitrary {@link ChordNode} that is part of the {@link ChordNetwork} this {@link ChordNode} wishes to join.
   */
  @Override
public void joinAndUpdate(ChordNode nprime) {
    if (nprime != null) {
      initFingerTable(nprime);
      // We need to do the delete of value before updating the tables otherwise it points to wrong node
      Map<String, String> temp_storage = new ConcurrentHashMap<>();
      ChordNode successor = this.fingerTable.node(1).get();
      for (String key : successor.keys()) {
        String value = successor.delete(this, key).get();
        temp_storage.put(key, value);
      }
      updateOthers();
      /* TODO: Move keys. */
      Identifier left_bound = this.predecessor().id();
      IdentifierCircularInterval interval = createLeftOpen(left_bound, this.id());
      for (String key : temp_storage.keySet()) {
        Identifier key_id = getNetwork().getIdentifierCircle().getIdentifierAt(Integer.parseInt(key));
        if (interval.contains(key_id)) {
          this.store(this, key, temp_storage.remove(key));
        } else {
          successor.store(this, key, temp_storage.remove(key));
        }
      }
    } else {
      for (int i = 1; i <= getNetwork().getNbits(); i++) {
        this.fingerTable.setNode(i, this);
      }
      this.setPredecessor(this);
    }
  }


  /**
   * Called on this {@link ChordNode} if it wishes to join the {@link ChordNetwork}. {@code nprime} references
   * another {@link ChordNode} that is already member of the {@link ChordNetwork}.
   *
   * Required for dynamic {@link ChordNetwork} mode. Since in that mode {@link ChordNode}s stabilize the network
   * periodically, this method simply sets its successor and waits for stabilization to do the rest.
   *
   * Defined in [1], Figure 7
   *
   * @param nprime Arbitrary {@link ChordNode} that is part of the {@link ChordNetwork} this {@link ChordNode} wishes to join.
   */
  @Override
  public void joinOnly(ChordNode nprime) {
    setPredecessor(null);
    if (nprime == null) {
      this.fingerTable.setNode(1, this);
    } else {
      this.fingerTable.setNode(1, nprime.findSuccessor(this,this));
    }
  }

  /**
   * Initializes this {@link ChordNode}'s {@link FingerTable} based on information derived from {@code nprime}.
   *
   * Defined in [1], Figure 6
   *
   * @param nprime Arbitrary {@link ChordNode} that is part of the network.
   */
  private void initFingerTable(ChordNode nprime) {
    /* TODO: Implementation required. */
    Identifier ident = getNetwork().getIdentifierCircle().getIdentifierAt(this.fingerTable.start(1));
    this.fingerTable.setNode(1, nprime.findSuccessor(this, ident));
    this.setPredecessor(this.successor().predecessor());
    this.successor().setPredecessor(this);

    for (int i = 1; i <= getNetwork().getNbits() - 1; i++) {
      ChordNode finger_i = this.fingerTable.node(i).get();
      Identifier start = getNetwork().getIdentifierCircle().getIdentifierAt(this.fingerTable.start(i + 1));
      if (createRightOpen(this.id(), finger_i.id()).contains(start)) {
        this.fingerTable.setNode(i + 1, finger_i);
      } else {
        start = getNetwork().getIdentifierCircle().getIdentifierAt(this.finger().start(i + 1));
        this.fingerTable.setNode(i + 1, nprime.findSuccessor(this, start));
      }
    }
  }

  /**
   * Updates all {@link ChordNode} whose {@link FingerTable} should refer to this {@link ChordNode}.
   *
   * Defined in [1], Figure 6
   */
  private void updateOthers() {
    /* TODO: Implementation required. */
    for (int i = 1; i <= getNetwork().getNbits(); i++) {
      Identifier ident = getNetwork().getIdentifierCircle().getIdentifierAt(
        this.id().getIndex() - (int) Math.pow(2, i - 1)
      );
      ChordNode p = this.findPredecessor(this, ident);
      // Edge case
      if (p.successor().id().equals(ident)) {
        p = p.successor();
      }
      p.updateFingerTable(this, i);
    }
  }

  /**
   * If node {@code s} is the i-th finger of this node, update this node's finger table with {@code s}
   *
   * Defined in [1], Figure 6
   *
   * @param s The should-be i-th finger of this node
   * @param i The index of {@code s} in this node's finger table
   */
  @Override
  public void updateFingerTable(ChordNode s, int i) {
    finger().node(i).ifPresent(node -> {
      /* TODO: Implementation required. */
      if (createLeftOpen(this.id(), node.id()).contains(s.id())) {
        this.fingerTable.setNode(i, s);
        ChordNode p = this.predecessor();
        p.updateFingerTable(s, i);
      }
    });
  }

  /**
   * Called by {@code nprime} if it thinks it might be this {@link ChordNode}'s predecessor. Updates predecessor
   * pointers accordingly, if required.
   *
   * Defined in [1], Figure 7
   *
   * @param nprime The alleged predecessor of this {@link ChordNode}
   */
  @Override
  public void notify(ChordNode nprime) {
    if (this.status() == NodeStatus.OFFLINE || this.status() == NodeStatus.JOINING) return;

    /* TODO: Implementation required. Hint: Null check on predecessor! */
    if (this.predecessor() == null || createOpen(this.predecessor().id(), this.id()).contains(nprime.id())) {
      this.setPredecessor(nprime);
    }

  }

  /**
   * Called periodically in order to refresh entries in this {@link ChordNode}'s {@link FingerTable}.
   *
   * Defined in [1], Figure 7
   */
  @Override
  public void fixFingers() {
    if (this.status() == NodeStatus.OFFLINE || this.status() == NodeStatus.JOINING) return;

    Random rand = new Random();
    int i = rand.nextInt(getNetwork().getNbits() - 1) + 2;
    Identifier id = getNetwork().getIdentifierCircle().getIdentifierAt(this.fingerTable.start(i));
    fingerTable.setNode(i, findSuccessor(this, id));
  }

  /**
   * Called periodically in order to verify this node's immediate successor and inform it about this
   * {@link ChordNode}'s presence,
   *
   * Defined in [1], Figure 7
   */
  @Override
  public void stabilize() {
    if (this.status() == NodeStatus.OFFLINE || this.status() == NodeStatus.JOINING) return;

    /* TODO: Implementation required.*/
     if (this.successor().predecessor() != null) {
      ChordNode x = this.successor().predecessor();
      if (createOpen(this.id(), this.successor().id()).contains(x.id())) {
        this.fingerTable.setNode(1, x);
      }
    }
    this.successor().notify(this);
  }

  /**
   * Called periodically in order to check activity of this {@link ChordNode}'s predecessor.
   *
   * Not part of [1]. Required for dynamic network to handle node failure.
   */
  @Override
  public void checkPredecessor() {
    if (this.status() == NodeStatus.OFFLINE || this.status() == NodeStatus.JOINING) return;

    /* TODO: Implementation required. Hint: Null check on predecessor! */
    if (this.predecessor() != null && this.predecessor().status() == NodeStatus.OFFLINE) {
      this.setPredecessor(this.findPredecessor(this, this));
    }
  }

  /**
   * Called periodically in order to check activity of this {@link ChordNode}'s successor.
   *
   * Not part of [1]. Required for dynamic network to handle node failure.
   */
  @Override
  public void checkSuccessor() {
    if (this.status() == NodeStatus.OFFLINE || this.status() == NodeStatus.JOINING) return;
    /* TODO: Implementation required. Hint: Null check on predecessor! */
     if (this.successor() != null && this.successor().status() == NodeStatus.OFFLINE) {
      if (this.predecessor() != null) {
        this.fingerTable.setNode(1, this.successor().successor());
      }
    }
  }

  /**
   * Performs a lookup for where the data with the provided key should be stored.
   *
   * @return Node in which to store the data with the provided key.
   */
  @Override
  protected ChordNode lookupNodeForItem(String key) {
    /* TODO: Implementation required. Hint: Null check on predecessor! */
    Identifier identifier = getNetwork().getIdentifierCircle().getIdentifierAt(Integer.parseInt(key));
    if (predecessor() != null) {
        return this.findSuccessor(this, identifier);
    }
    return this;
  }

  @Override
  public String toString() {
    return String.format("ChordPeer{id=%d}", this.id().getIndex());
  }
}
