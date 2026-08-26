import i18n, {
  supportedLanguages,
  changeLanguage,
  getDeviceLanguage,
  initI18n,
} from "../i18n";

describe("i18n Localization", () => {
  beforeAll(async () => {
    await initI18n();
  });

  it("supports English, Hindi, and Urdu", () => {
    const codes = supportedLanguages.map((l) => l.code);
    expect(codes).toContain("en");
    expect(codes).toContain("hi");
    expect(codes).toContain("ur");
  });

  it("identifies Urdu as RTL", () => {
    const urdu = supportedLanguages.find((l) => l.code === "ur");
    expect(urdu?.isRTL).toBe(true);

    const english = supportedLanguages.find((l) => l.code === "en");
    expect(english?.isRTL).toBe(false);
  });

  it("translates common keys into English", async () => {
    await changeLanguage("en");
    expect(i18n.t("common.ok")).toBe("OK");
    expect(i18n.t("common.cancel")).toBe("Cancel");
    expect(i18n.t("home.title")).toBe("DoonJuma");
  });

  it("translates common keys into Hindi", async () => {
    await changeLanguage("hi");
    expect(i18n.t("common.ok")).toBe("ठीक है");
    expect(i18n.t("common.cancel")).toBe("रद्द करें");
    expect(i18n.t("home.title")).toBe("दून जुमा");
  });

  it("translates common keys into Urdu", async () => {
    await changeLanguage("ur");
    expect(i18n.t("common.ok")).toBe("ٹھیک ہے");
    expect(i18n.t("home.title")).toBe("دون جمعہ");
  });
});
