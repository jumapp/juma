import {
  enqueueMutation,
  getOutbox,
  clearOutbox,
  removeMutation,
} from "../services/sync/outbox";

describe("Offline Outbox Queue", () => {
  beforeEach(async () => {
    await clearOutbox();
  });

  it("enqueues mutations with generated UUIDs and queued status", async () => {
    const item = await enqueueMutation("masjid", "CREATE", {
      name: "Offline Masjid 1",
      city: "Dehradun",
    });

    expect(item.id).toBeDefined();
    expect(item.entity).toBe("masjid");
    expect(item.type).toBe("CREATE");
    expect(item.status).toBe("queued");
    expect(item.payload.name).toBe("Offline Masjid 1");

    const outbox = await getOutbox();
    expect(outbox).toHaveLength(1);
    expect(outbox[0].id).toBe(item.id);
  });

  it("enqueues multiple mutations in FIFO order", async () => {
    await enqueueMutation("masjid", "CREATE", { name: "Masjid 1" });
    await enqueueMutation("salat_schedule", "UPDATE", { salat_name: "fajr" });
    await enqueueMutation("program", "CREATE", { name: "Maktab" });

    const outbox = await getOutbox();
    expect(outbox).toHaveLength(3);
    expect(outbox[0].entity).toBe("masjid");
    expect(outbox[1].entity).toBe("salat_schedule");
    expect(outbox[2].entity).toBe("program");
  });

  it("removes a mutation by ID", async () => {
    const item1 = await enqueueMutation("masjid", "CREATE", { name: "Masjid 1" });
    const item2 = await enqueueMutation("masjid", "CREATE", { name: "Masjid 2" });

    await removeMutation(item1.id);

    const outbox = await getOutbox();
    expect(outbox).toHaveLength(1);
    expect(outbox[0].id).toBe(item2.id);
  });

  it("clears entire outbox", async () => {
    await enqueueMutation("masjid", "CREATE", { name: "Masjid 1" });
    await enqueueMutation("masjid", "CREATE", { name: "Masjid 2" });

    await clearOutbox();

    const outbox = await getOutbox();
    expect(outbox).toHaveLength(0);
  });
});
